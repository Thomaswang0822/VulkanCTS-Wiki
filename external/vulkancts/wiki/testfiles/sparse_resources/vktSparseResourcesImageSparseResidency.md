# vktSparseResourcesImageSparseResidency.cpp

## Overview

[`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1-L22) implements `sparse_resources.image_sparse_residency` and `sparse_resources.device_group_image_sparse_residency`, using sparse image residency binds, compute shaders, and readback checks to verify resident and nonresident sparse blocks ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L365-L678), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L904-L1205)). The same file also adds a non-device-group `mutable` subtree for sparse mutable-format images ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2084-L2135)). The Vulkan API test plan identifies sparse resources as a separate feature area, but leaves detailed sparse-resource behavior to implementation files such as this one ([`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276)).

## Role

Implementation-heavy registration file for partially resident sparse images. The regular root includes the direct `mutable` child; the device-group root uses the same common residency builder with `useDeviceGroup=true` and skips `mutable` ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2025-L2028), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2084-L2086), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2140-L2149)).

## Source Code

- Primary source: [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1)
- Shared image/type helpers: [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L43-L115), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L52-L118)

## Registration Hierarchy

```text
sparse_resources.image_sparse_residency
├── 2d
├── 2d_array
├── cube
├── cube_array
├── 3d
└── mutable
```

## Test Families

### 2d — partially resident 2D storage images

The `2d` child is generated with sizes `512x256x1`, `1024x128x1`, and `11x137x1`, using sparse-residency formats plus `VK_FORMAT_A8_UNORM_KHR` for non-device-group regular cases outside Vulkan SC ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1213-L1220), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2029-L2036)). The instance binds only even-numbered sparse blocks for resident mips, binds miptails and metadata when present, writes with a generated compute shader, and checks resident blocks against coordinate-derived values while expecting zeros in nonresident blocks only when `residencyNonResidentStrict` is true ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L523-L555), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L904-L1123)).

### 2d_array — partially resident 2D array storage images

The `2d_array` child uses sizes `512x256x6`, `1024x128x8`, and `11x137x3`; shared layer logic maps the third component to array layers ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2034-L2036), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L182-L205)). The shader grid and validation account for array layers through shared image-size helpers ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L175-L183), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L955-L977)).

### cube — partially resident cube images

The `cube` child uses sizes `256x256x1`, `128x128x1`, and `137x137x1`, sets cube-compatible image creation flags, and otherwise follows the same sparse residency path ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2037-L2039), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L416-L419)).

### cube_array — partially resident cube-array images

The `cube_array` child uses sizes `256x256x6`, `128x128x8`, and `137x137x3`; shared helper logic expands cube-array layers by six faces per array element ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2040-L2042), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L196-L200)).

### 3d — partially resident 3D storage images

The `3d` child uses sizes `512x256x16`, `1024x128x8`, and `11x137x3`, maps to `VK_IMAGE_TYPE_3D`, and requires sparse residency support for 3D image types ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2043-L2045), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L390-L407), [`vktSparseResourcesTestsUtil.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.cpp#L1186-L1203)).

### mutable — sparse mutable-format image views

The `mutable` child is added only for the non-device-group root ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2084-L2135)). It covers 2D, 2D array, and 3D image types with format triples where the base image format differs from both view formats and compatible pixel sizes are required; R64, alpha-only, and YCbCr formats are filtered out ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1992-L2012), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2087-L2127)). The mutable instance allocates the left half of the image, writes upper and lower portions through two storage-image views, copies the written portions out, and compares integer or floating-point expected images with zero or `0.01` thresholds ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1490-L1575), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1577-L1989)).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Registered roots | `image_sparse_residency` and `device_group_image_sparse_residency` are separate factories sharing the common builder ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2140-L2149)). |
| Regular direct children | `2d`, `2d_array`, `cube`, `cube_array`, `3d`, and `mutable` are direct children of the regular root ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2029-L2135)). |
| Device-group direct children | The device-group root has the same five image-type children but skips `mutable` because `mutable` is guarded by `if (!useDeviceGroup)` ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2084-L2086), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2146-L2149)). |
| Image sizes | Regular residency image types each have three sizes; mutable has one size for each of 2D, 2D array, and 3D ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2030-L2045), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2087-L2091)). |
| Formats | Residency formats come from `getTestFormats()` plus optional `VK_FORMAT_A8_UNORM_KHR`; mutable formats filter out R64, alpha-only, and YCbCr formats ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1213-L1220), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1992-L2007)). |

## Support / Feature Requirements

Regular residency cases require supported image sizes, sparse support for the image type, storage-image support for the selected format or storage-compatible plane formats, maintenance5 plus write-without-format support for `VK_FORMAT_A8_UNORM_KHR`, and shader-image-int64 plus sparse-image-int64 atomic features for R64 formats ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L276-L337)). Iteration requires sparse-binding and compute queues, sparse image-format support, memory within `sparseAddressSpaceSize`, matching memory types, and peer memory features for device-group mode ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L371-L377), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L439-L480)). Mutable cases require sparse image type support, storage-image support for image and view formats, sparse format support, and sparse+mutable image format properties ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1293-L1340)).

## Verification Methods

Regular residency tests generate a compute shader per plane, write coordinate-derived values into resident sparse blocks, copy each plane to a host buffer, log channel images, and validate integer, fixed-point, or floating-point channels with format-aware error handling ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L175-L273), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L712-L808), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L882-L1205)). Mutable tests compare copied portions against generated expected images using `tcu::intThresholdCompare` or `tcu::floatThresholdCompare` ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1446-L1475), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1508-L1575)).

## Test Principles Observed

- Sparse residency is tested by intentionally binding alternating sparse blocks and checking both resident data and strict nonresident zero behavior when the device advertises strict behavior ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L531-L555), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L1066-L1123)).
- Multi-planar and storage-compatible formats are handled per plane, with per-plane shaders and image views ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L209-L273), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L712-L759)).
- Device-group coverage reuses the same image-type matrix but routes sparse binding through device-group sparse-bind metadata and omits the mutable subtree ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L632-L641), [`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2084-L2086)).

## Notes / Uncertainties

- The canonical hierarchy above is for `sparse_resources.image_sparse_residency`; the inspected file also registers `sparse_resources.device_group_image_sparse_residency` with `2d`, `2d_array`, `cube`, `cube_array`, and `3d` direct children, but without `mutable` ([`vktSparseResourcesImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageSparseResidency.cpp#L2140-L2149)).
