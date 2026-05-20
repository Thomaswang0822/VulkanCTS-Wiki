# vktSparseResourcesMipmapSparseResidency.cpp

## Overview

[`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L1-L22) implements `sparse_resources.mipmap_sparse_residency` and `sparse_resources.device_group_mipmap_sparse_residency`, binding sparse image blocks and mip tails across all mip levels and validating copy/readback data ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L135-L409), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L411-L582)). The Vulkan API test plan identifies sparse resources as a distinct feature area; this file supplies concrete mipmapped sparse-image residency coverage ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276)).

## Role

Implementation-heavy registration file for mipmapped sparse image residency. The same common builder is used for the regular and device-group roots, with device-group mode enabled only by `createDeviceGroupMipmapSparseResidencyTests()` ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L592-L660)).

## Source Code

- Primary source: [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L1)
- Shared image/type helpers: [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L78-L115), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118)
- Test-plan context: [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276)

## Registration Hierarchy

```text
sparse_resources.mipmap_sparse_residency
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

## Test Families

### 2d — mipmapped 2D sparse residency

The `2d` child is generated with sizes `512x256x1`, `1024x128x1`, and `11x137x1`, with formats from `getTestFormats(IMAGE_TYPE_2D)` and leaves named by image size under each format ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L596-L641)). The test computes the mip count from image format properties, binds each sparse-resident mip level before the mip tail, binds mip-tail and metadata memory as required, then copies all mip levels to and from buffers ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L186-L198), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L242-L409), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L411-L540)).

### 2d_array — mipmapped 2D array sparse residency

The `2d_array` child uses sizes `512x256x6`, `1024x128x8`, and `11x137x3`, with shared layer-count behavior mapping the third coordinate to array layers ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L600-L602), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L182-L205)).

### cube — mipmapped cube sparse residency

The `cube` child uses sizes `256x256x1`, `128x128x1`, and `137x137x1`; cube-compatible image flags are added before sparse format support and mip-count calculation ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L603-L605), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L177-L198)).

### cube_array — mipmapped cube-array sparse residency

The `cube_array` child uses sizes `256x256x6`, `128x128x8`, and `137x137x3`, with cube-array layer counts supplied by shared helpers and all mip levels included in each copy region ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L606-L608), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L196-L200), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L419-L446)).

### 3d — mipmapped 3D sparse residency

The `3d` child uses sizes `256x256x16`, `1024x128x8`, and `11x137x3`, maps to 3D images, and uses all generated mip levels in sparse binds and copy/readback validation ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L609-L611), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L267-L287), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L568-L579)).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Registered roots | `mipmap_sparse_residency` and `device_group_mipmap_sparse_residency` are separate factories sharing the common builder ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L651-L660)). |
| Direct children | `2d`, `2d_array`, `cube`, `cube_array`, and `3d` are generated from `imageParameters` ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L596-L617)). |
| Image sizes | Three sizes per image type are registered, including odd-size cases such as `11x137x*` after format alignment filtering ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L596-L611), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L626-L641)). |
| Formats | Formats are the shared sparse image format list, with YCbCr formats included only for 2D and 2D array by `getTestFormats()` ([`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118)). |
| Mip levels | Mip level count is derived at runtime with `getMipmapCount()` from image format properties and image extent ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L186-L198)). |

## Support / Feature Requirements

The case checks image-size limits, sparse support for the image type, and R64 sparse-image int64 atomic support in `checkSupport()` ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L85-L107)). Iteration requires sparse-binding and compute queues, sparse image format support, memory within `sparseAddressSpaceSize`, a matching memory type, and peer copy features for device-group mode ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L137-L145), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L182-L240)).

## Verification Methods

Each case allocates and binds sparse memory for resident mip levels, miptails, and metadata, then signals a sparse-bind semaphore before transfer work reads from the image ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L242-L409), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L554-L558)). The test fills a host-visible input buffer with deterministic bytes, copies all planes and mips into the image and back out, invalidates the output allocation, and compares every mip-level byte range with `deMemCmp` ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L411-L475), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L508-L582)).

## Test Principles Observed

- Mipmapped sparse residency is tested by binding normal sparse image blocks up to `imageMipTailFirstLod` and separately handling single or per-layer mip tails and metadata ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L267-L360)).
- The regular and device-group roots share the same generated image-type, format, and size matrix; device-group mode only changes bind/submit device targeting ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L362-L382), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L651-L660)).
- Verification covers all generated mip levels and planes rather than only the base level ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L413-L446), [`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L568-L579)).

## Notes / Uncertainties

- The canonical hierarchy above is for `sparse_resources.mipmap_sparse_residency`; the inspected file also registers `sparse_resources.device_group_mipmap_sparse_residency` with the same five direct children ([`vktSparseResourcesMipmapSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMipmapSparseResidency.cpp#L651-L660)).
