## Overview

**Core question:** Can a sparse mipmapped image preserve data across every resident mip level, mip tail, plane, and supported image type?

- [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L135-L201) implements the `sparse_resources.mipmap_sparse_residency` and `sparse_resources.device_group_mipmap_sparse_residency` test families.
- Each test case creates a single-sampled sparse image, binds the memory reported for its mip levels, mip tails, and metadata, then copies every plane and mip level through buffers.
- The host compares the returned bytes with the input pattern. The page explains the image-type matrix, residency binding, transfer flow, and failure interpretation.

## Background Knowledge

- A sparse image reserves virtual address space while the application binds physical memory to selected regions. Mip levels before `imageMipTailFirstLod` use sparse image blocks; smaller levels occupy a mip tail. [`sparsemem.adoc`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L867-L914)
- A format can expose multiple image aspects or planes, each with separate sparse requirements. Metadata is a separate aspect when reported and must be bound before the device uses the image. [`sparsemem.adoc`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L497-L536)

## Registration Hierarchy

```text
sparse_resources.mipmap_sparse_residency
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

The source registers the same five direct children under `sparse_resources.device_group_mipmap_sparse_residency`. Each child contains format groups and generated test case leaves named from the image extent.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `mipmap_sparse_residency`, `device_group_mipmap_sparse_residency` | Selects regular or device-group sparse binding and submission; both use the same matrix. | [`createMipmapSparseResidencyTests()` and device-group factory](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L651-L660) |
| Image type | `2d`, `2d_array`, `cube`, `cube_array`, `3d` | Changes image dimensionality, layer interpretation, and mip extents. | [`createMipmapSparseResidencyTestsCommon()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L592-L617) |
| Image extent | `512x256x1`, `1024x128x1`, `11x137x1` for `2d`; `512x256x6`, `1024x128x8`, `11x137x3` for `2d_array`; `256x256x1`, `128x128x1`, `137x137x1` for `cube`; `256x256x6`, `128x128x8`, `137x137x3` for `cube_array`; `256x256x16`, `1024x128x8`, `11x137x3` for `3d` | Exercises ordinary and non-power-of-two dimensions. The third coordinate represents layers for array and cube-array images, and depth for 3D images. | [`imageParameters`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L596-L611) |
| Format | `getTestFormats(imageType)` | Changes plane count, alignment, sparse requirements, and copy extents. YCbCr formats are limited by the shared helper. | [`getTestFormats()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118) |
| Mip levels | Runtime count from `getMipmapCount()` | Determines the non-tail block binds, tail boundary, and copy list. | [`getMipmapCount()` call](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L182-L198) |

The generator skips an extent when its width or height is not compatible with the format's image-size alignment. This pruning particularly affects some YCbCr cases. [`createMipmapSparseResidencyTestsCommon()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L619-L641)

## Behavior Parameters

The primary behavioral axis is the registered image type. It changes the image's dimensional and layer model while the test keeps the same residency and transfer contract.

### `2d` : mipmapped 2D image

The test uses extents `512x256x1`, `1024x128x1`, and `11x137x1`. It binds each non-tail mip block and the reported tail and checks all generated mips through buffer-image copies.

### `2d_array` : mipmapped 2D array image

The extents use six, eight, or three array layers. Binding and copy subresources must address every layer in the array.

### `cube` : mipmapped cube image

The test adds `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` and uses square extents. Cube faces are represented through the image's array layers, so all faces participate in the same residency and copy checks.

### `cube_array` : mipmapped cube-array image

The extents use six, eight, or three layers. The test combines cube-compatible setup with the array-layer handling used by the shared image helpers.

### `3d` : mipmapped 3D image

The extents include depths `16`, `8`, and `3`. Mip extents reduce in three dimensions, and the test binds and copies the resulting 3D mip regions.

## Shader Analysis

This implementation does not use shaders or generated program artifacts. It verifies the sparse image with transfer commands and host-side byte comparison.

## Runtime Execution and Result Checking

- `checkSupport()` rejects image extents beyond device limits, image types without sparse support, and unsupported sparse image formats. R64 formats also require `VK_EXT_shader_image_atomic_int64` with `sparseImageInt64Atomics` enabled. [`checkSupport()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L85-L107)
- The instance creates one sparse-binding queue and one compute-capable queue. It creates an optimal-tiled image with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT` and transfer source and destination usage. [`iterate()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L135-L201)
- For each aspect and image layer, the instance binds every block in each mip before `imageMipTailFirstLod`. It then binds a per-layer or shared mip tail according to `VK_SPARSE_IMAGE_FORMAT_SINGLE_MIPTAIL_BIT`. If metadata requirements exist, it binds the metadata tail with `VK_SPARSE_MEMORY_BIND_METADATA_BIT`. [`iterate()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L242-L360)
- The sparse bind submission signals a semaphore. Transfer commands wait for that bind, copy the deterministic input buffer into every plane and mip, and copy the image back into the output buffer. [`iterate()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L362-L508)
- After completion, the host invalidates the output allocation and compares each byte with `deMemCmp`. A mismatch fails the case; a complete comparison returns `Passed`. [`iterate()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L508-L582)
- Device-group mode uses the same image and extent matrix but changes the physical-device selection and bind/submit device targeting. [`createDeviceGroupMipmapSparseResidencyTests()`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L657-L660)

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `2d` | Incorrect sparse block, mip-tail, plane, or transfer handling for a 2D image |
| `2d_array` | Incorrect layer addressing or per-layer sparse binding for a 2D array |
| `cube` | Incorrect cube-compatible image setup, face/layer handling, or mip binding |
| `cube_array` | Incorrect cube-array layer or mip-tail handling |
| `3d` | Incorrect 3D extent, depth reduction across mips, or sparse binding handling |

All image types share common failure causes: unsupported sparse format properties, an invalid memory type or allocation size, incorrect synchronization after `queueBindSparse`, or data corruption during an image-to-buffer or buffer-to-image copy.

### Cause Analysis

#### Incomplete or incorrect sparse memory binding

**Possible failure symptoms:** The returned data differs from the input pattern in one or more mip levels, layers, or planes.

**Possible implementation causes:** The implementation may interpret `imageGranularity`, `imageMipTailFirstLod`, tail stride, aspect requirements, or metadata binding incorrectly. The source obtains these values from Vulkan queries and binds the regions before transfer use. The exact failing mapping requires source-level investigation of the reported sparse requirements and bind processing.

#### Incorrect image-type or layer addressing

**Possible failure symptoms:** Failures cluster in array layers, cube faces, cube-array faces, or 3D mips while other regions compare correctly.

**Possible implementation causes:** The image extent, array-layer count, subresource layer range, or 3D mip extent may not match the image type. The Vulkan specification defines image subresources and sparse image coordinates separately for these image classes, so the implementation-level cause needs investigation from the failing case and reported properties.

#### Transfer ordering or data movement error

**Possible failure symptoms:** The output buffer contains stale, incomplete, or otherwise different bytes even though the sparse binds appear to cover the requested regions.

**Possible implementation causes:** The sparse bind signal, transfer barriers, image layouts, or copy regions may not establish the required ordering or may address a different aspect or mip. The source explicitly waits on the bind semaphore and compares every generated copy range; further attribution requires investigation of the failing synchronization or copy operation.

#### Device-group targeting error

**Possible failure symptoms:** A case fails only under `device_group_mipmap_sparse_residency`, with mismatches that depend on the physical-device iteration.

**Possible implementation causes:** Sparse binds or transfer work may target different physical devices, or peer-copy support may not cover the selected device pair. The source chooses a first and second device for each physical-device iteration; the precise implementation cause requires investigation of the failing device pair.

## Case Pruning

- `checkSupport()` prunes unsupported image sizes, image types, sparse formats, and the R64 atomic feature combination with `NotSupportedError`.
- The generator prunes an image extent when its width or height is not a multiple of the format's required alignment. This prevents invalid YCbCr extent cases while retaining the registered matrix for compatible formats.
- The test does not prune individual mip levels. It derives the mip count from image format properties and validates every resulting level.

## Key Takeaways

- The test covers both non-tail mip blocks and mip tails, including metadata aspects when the implementation reports them.
- The primary behavior choice is image type: the same transfer-based residency check is applied to 2D, array, cube, cube-array, and 3D images.
- The pass condition is byte-for-byte equality for every copied plane and mip level after sparse binding completes.
- Device-group cases reuse the matrix and add device-targeting coverage.

## Source Reference Appendix

- Implementation and support checks: [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L1-L107)
- Runtime binding and transfer validation: [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L135-L582)
- Registration and parameter generation: [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L592-L660)
- Shared image and format helpers: [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L78-L115), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118)
- Vulkan sparse image semantics: [`sparsemem.adoc`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L497-L536), [`sparsemem.adoc`](../../../../vulkan-docs/src/chapters/sparsemem.adoc#L867-L914)
- Mustpass registration: [`sparse-resources.txt`](../../../mustpass/main/vk-default/sparse-resources.txt)
