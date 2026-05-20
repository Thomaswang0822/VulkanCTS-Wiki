# vktSparseResourcesImageRebind.cpp

## Overview

[`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L1-L44) implements the `sparse_resources.image_rebind` branch registered by the sparse-resource dispatcher ([`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L63), [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L900-L903)). The file summary describes rebinding a sparse image from one memory object to another, then rebinding one sparse block from the first object back into a selected layer and validating the resulting mixed contents ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L23-L43)).

## Role

Implementation-heavy Level-3 registration file for sparse image rebind behavior. It constructs the `image_rebind` root and generates direct children by image type, then formats and image sizes below each child ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L843-L897), [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L900-L903)).

## Source Code

- Primary source: [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L1)
- Shared image/type helpers: [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L73-L115)
- Shared queue/device base: [`vktSparseResourcesBase.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.hpp#L59-L114)
- Test-plan context: [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L257-L276)

## Registration Hierarchy

```text
sparse_resources.image_rebind
├── 2d
├── 2d_array
├── cube
├── cube_array
└── 3d
```

## Test Families

### 2d — two-dimensional sparse image rebind cases

This direct child is generated from `IMAGE_TYPE_2D`, with three image sizes and all non-YCbCr test formats returned for the image type ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L847-L890)). Runtime creates a 2D sparse image using `VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT`, prepares full sparse-block binding tables for two memory objects, and prepares one partial bind for the selected layer ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L226-L258), [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L307-L419)).

### 2d_array — two-dimensional array sparse image rebind cases

This child is generated from `IMAGE_TYPE_2D_ARRAY`, with sizes such as `512x256x6`, `128x128x8`, and `503x137x3` where the `z` component supplies layer count ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L851-L853)). The partial rebind targets `partiallyBoundLayer = arrayLayers - 1`, so array-style cases validate rebinding in a selected layer rather than only in the first layer ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L307-L315), [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L374-L415)).

### cube — cube sparse image rebind cases

This child is generated from `IMAGE_TYPE_CUBE`; cube-compatible image types add `VK_IMAGE_CREATE_CUBE_COMPATIBLE_BIT` before sparse support checks ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L854-L856), [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L242-L247)).

### cube_array — cube-array sparse image rebind cases

This child is generated from `IMAGE_TYPE_CUBE_ARRAY`, sharing the cube-compatible path and the selected-layer partial rebind logic ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L857-L859), [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L242-L247)).

### 3d — three-dimensional sparse image rebind cases

This child is generated from `IMAGE_TYPE_3D` with depth-bearing sizes such as `256x256x16`, `128x128x8`, and `503x137x3` ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L860-L862)). Partial-bind offsets can advance in x, y, and z when the sparse-block counts allow it ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L377-L405)).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Direct children | `2d`, `2d_array`, `cube`, `cube_array`, and `3d` are generated from the `imageParameters` vector ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L847-L868)). |
| Image sizes | Each image type registers three sizes; the smallest odd-size fourth case used by aliasing/residency generators is not present in this file ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L847-L862)). |
| Formats | Formats come from `getTestFormats(imageType)`, but `isYCbCrFormat(format)` cases are skipped for this rebind branch ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L870-L879)). |
| Memory objects | The rebind algorithm uses exactly two backing memory objects, controlled by `kMemoryObjectCount = 2` ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L89), [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L421-L448)). |

## Support / Feature Requirements

Each case requires `sparseResidencyAliased`, checks image-size limits, and checks sparse support for the image type ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L118-L132)). Runtime requires sparse-binding and transfer queues, checks sparse support for the concrete image format, rejects unsupported `getPhysicalDeviceImageFormatProperties` results, checks `sparseAddressSpaceSize`, selects a memory type, and verifies peer-memory copy/generic-destination support for cross-device iterations ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L194-L206), [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L245-L301)). It also rejects image sizes with fewer than two sparse blocks and formats whose mip level 0 is already in the mip tail, because those cannot exercise a partial sparse-block rebind ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L327-L336)).

## Verification Methods

The test fully binds memory object 0, clears the image with color 0, fully binds memory object 1 and clears with color 1, then partially rebinds one block from memory object 0 before copying the selected layer to a host-visible buffer ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L455-L626), [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L629-L714)). Verification walks every texel in the copied layer and expects color 0 inside the partial-bind extent and color 1 outside it, using exact integer comparisons and fixed/floating comparisons with format-appropriate error tolerance ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L723-L833)).

## Test Principles Observed

- The test is intentionally stateful: it proves that a later sparse bind replaces earlier bindings for the same image ranges, then that a smaller bind can restore one block from the old memory object ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L455-L626)).
- Validation is spatial, not just whole-image equality: the expected value changes at the exact partial sparse-block extent computed from image granularity and sparse-block counts ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L374-L415), [`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L745-L774)).

## Notes / Uncertainties

- The common builder accepts a `useDeviceGroup` parameter, and runtime has device-group paths, but the inspected file only exposes the regular `image_rebind` factory in this sparse-resource root ([`vktSparseResourcesImageRebind.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesImageRebind.cpp#L843-L903)).
