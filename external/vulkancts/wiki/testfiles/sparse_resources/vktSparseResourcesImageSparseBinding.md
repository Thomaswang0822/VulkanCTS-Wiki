# vktSparseResourcesImageSparseBinding.cpp

## Overview

[`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L1-L22) implements the `sparse_resources.image_sparse_binding` and `sparse_resources.device_group_image_sparse_binding` top-level branches registered by the sparse-resource dispatcher ([`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L50-L51), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L711-L720)). The Vulkan API test plan identifies sparse resources as a distinct feature area, while this source provides concrete coverage for fully bound sparse images using several `vkQueueBindSparse` packaging styles ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L257-L417)).

## Role

Implementation-heavy registration file for fully resident sparse-image binding. The same common builder is used for the regular root and for the device-group root, with `useDeviceGroup=true` only in the latter factory ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L631-L633), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L717-L720)).

## Source Code

- Primary source: [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L1)
- Shared image/type helpers: [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L43-L115), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118)

## Registration Hierarchy

```text
sparse_resources.image_sparse_binding
├── multiple_sparse_memory_bind
├── multiple_sparse_image_opaque_memory_bind_info
└── multiple_bind_sparse_info
```

## Test Families

### multiple_sparse_memory_bind — one opaque-bind info with many memory binds

This direct child comes from `toString(MULTIPLE_SPARSE_MEMORY_BIND)` in the `bindTypes` array ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L58-L82), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L658-L665)). Each case creates a sparse optimal image with `VK_IMAGE_CREATE_SPARSE_BINDING_BIT`, computes mip levels from `getMipmapCount()`, allocates one `VkSparseMemoryBind` per alignment-sized range, wraps all binds in one `VkSparseImageOpaqueMemoryBindInfo`, and submits one `VkBindSparseInfo` ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L180-L214), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L221-L303)).

### multiple_sparse_image_opaque_memory_bind_info — many opaque-bind info records

This child uses the same image and memory setup but creates one `VkSparseImageOpaqueMemoryBindInfo` per sparse bind, then submits them through a single `VkBindSparseInfo` whose `imageOpaqueBindCount` equals `numSparseBinds` ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L307-L357)). The registered tree nests generated cases under image type, format, and image-size names ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L666-L705)).

### multiple_bind_sparse_info — many bind-sparse submissions in one queue call

This child creates one `VkBindSparseInfo` per sparse image opaque bind and passes the vector to `queueBindSparse` with `bindSparseInfoCount == numSparseBinds` ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L360-L415)). The device-group factory registers `sparse_resources.device_group_image_sparse_binding` with the same direct children and adds `VkDeviceGroupBindSparseInfo` to the `pNext` chain when `m_useDeviceGroups` is true ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L279-L299), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L717-L720)).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Registered roots | `image_sparse_binding` and `device_group_image_sparse_binding` are constructed by separate factories that call the same common builder ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L711-L720)). |
| Direct children | `multiple_sparse_memory_bind`, `multiple_sparse_image_opaque_memory_bind_info`, and `multiple_bind_sparse_info` come from the `BindType` string table and loop over `bindTypes` ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L73-L82), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L658-L665)). |
| Image types | 1D, 1D array, 2D, 2D array, 3D, cube, and cube array are registered through `imageParameters` ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L635-L656)). |
| Image sizes | Each image type has three sizes, including regular powers-of-two and odd dimensions such as `11x137x*`; YCbCr-incompatible odd sizes are skipped by alignment checks ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L635-L656), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L679-L688)). |
| Formats | Formats come from `getTestFormats()`; non-device-group regular cases append `VK_FORMAT_A8_UNORM_KHR` outside Vulkan SC ([`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L619-L626)). |

## Support / Feature Requirements

The case requires `sparseBinding`, checks image-size limits, requires `VK_KHR_maintenance5` for `VK_FORMAT_A8_UNORM_KHR`, and requires `VK_EXT_shader_image_atomic_int64` plus `sparseImageInt64Atomics` for R64 formats ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L107-L129)). Runtime setup requires sparse-binding and compute queues, checks image-format sparse binding support through `getPhysicalDeviceImageFormatProperties`, rejects allocations larger than `sparseAddressSpaceSize`, selects a memory type, and checks peer copy features for device-group cross-device memory ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L156-L163), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L202-L255)).

## Verification Methods

After sparse binding, each case writes a deterministic byte pattern to a host-visible input buffer, copies buffer-to-image and image-to-buffer over every plane and mip level, invalidates the output allocation, and compares bytes against the reference data ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L429-L488), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L520-L604)). For formats where low bits are explicitly don't-care, the comparison masks the least-significant 6 or 4 bits before deciding failure ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L576-L604)).

## Test Principles Observed

- The file separates sparse image memory coverage by how binds are packaged for `vkQueueBindSparse`, not by different shader algorithms ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L257-L417)).
- The regular and device-group roots intentionally share parameter generation while device-group mode changes sparse-bind and submit metadata ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L631-L633), [`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L279-L299)).
- Verification is data-path based: successful sparse binding is not enough; copied-back image contents must match the reference bytes ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L589-L604)).

## Notes / Uncertainties

- The canonical hierarchy above is for `sparse_resources.image_sparse_binding`; the inspected file also registers `sparse_resources.device_group_image_sparse_binding` with the same three direct children ([`vktSparseResourcesImageSparseBinding.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseBinding.cpp#L711-L720)).
