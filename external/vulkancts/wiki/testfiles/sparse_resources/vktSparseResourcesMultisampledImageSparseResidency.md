# vktSparseResourcesMultisampledImageSparseResidency.cpp

## Overview

[`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L1-L43) implements the `sparse_resources.multisampled_image_sparse_residency` top-level branch registered by the sparse-resource dispatcher ([`vktSparseResourcesTests.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTests.cpp#L59), [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L806-L809)). The source explicitly describes a partially resident multisampled image where the lowest row of sparse tiles is not bound and nonresident accesses are expected to produce zero under strict residency behavior ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L23-L41)).

## Role

Implementation-heavy Level-3 registration file. It constructs the `multisampled_image_sparse_residency` group and registers one direct child per image format, with sample-count cases nested under each format ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L769-L803), [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L806-L809)).

## Source Code

- Primary source: [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L1)
- Shared sparse-resource helpers: [`vktSparseResourcesTestsUtil.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesTestsUtil.hpp#L161-L204), [`vktSparseResourcesBase.hpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesBase.hpp#L59-L114)
- Test-plan context: [`apitests.adoc`](../../../../../doc/testspecs/VK/apitests.adoc#L273-L276)

## Registration Hierarchy

```text
sparse_resources.multisampled_image_sparse_residency
├── rgba32f
├── rgba16f
├── r32f
├── rgba32ui
├── rgba16ui
├── rgba8ui
├── r32ui
├── rgba32i
├── rgba16i
├── rgba8i
└── r32i
```

## Test Families

### rgba32f — floating-point RGBA32 multisample sparse-residency cases

This direct child is generated from `VK_FORMAT_R32G32B32A32_SFLOAT`; nested cases are `samples_2`, `samples_4`, `samples_8`, and `samples_16` ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L772-L797)). The generated compute shader uses `GL_ARB_sparse_texture2`, writes to an `image2DMS`, reads with `sparseImageLoadARB`, maps nonresident texels to zero, and stores the observed value in an `r32ui` result image ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L272-L306)).

### rgba16f — floating-point RGBA16 multisample sparse-residency cases

This child uses `VK_FORMAT_R16G16B16A16_SFLOAT` and the same four sample-count cases as the other format groups ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L772-L797)).

### r32f — floating-point R32 multisample sparse-residency cases

This child uses `VK_FORMAT_R32_SFLOAT` with the fixed `256x512x1` image size selected by the common builder ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L772-L797)).

### rgba32ui — unsigned-integer RGBA32 multisample sparse-residency cases

This child is generated from `VK_FORMAT_R32G32B32A32_UINT`; unsigned formats receive `u` shader type prefixes through `getFormatPrefix()` ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L159-L182), [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L281-L303)).

### rgba16ui — unsigned-integer RGBA16 multisample sparse-residency cases

This child is generated from `VK_FORMAT_R16G16B16A16_UINT` and shares the same sparse-residency bind pattern as the other formats ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L775-L797)).

### rgba8ui — unsigned-integer RGBA8 multisample sparse-residency cases

This child is generated from `VK_FORMAT_R8G8B8A8_UINT` and receives all four sample-count cases ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L775-L797)).

### r32ui — unsigned-integer R32 multisample sparse-residency cases

This child is generated from `VK_FORMAT_R32_UINT`; the result image is also `VK_FORMAT_R32_UINT` and stores the value interpreted from shader output ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L284-L303), [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L463-L468)).

### rgba32i — signed-integer RGBA32 multisample sparse-residency cases

This child is generated from `VK_FORMAT_R32G32B32A32_SINT`; signed integer formats receive `i` shader type prefixes through `getFormatPrefix()` ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L172-L176), [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L281-L303)).

### rgba16i — signed-integer RGBA16 multisample sparse-residency cases

This child is generated from `VK_FORMAT_R16G16B16A16_SINT` and follows the same four sample-count matrix ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L777-L797)).

### rgba8i — signed-integer RGBA8 multisample sparse-residency cases

This child is generated from `VK_FORMAT_R8G8B8A8_SINT` and uses the common partial-residency execution path ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L777-L797)).

### r32i — signed-integer R32 multisample sparse-residency cases

This child is generated from `VK_FORMAT_R32_SINT` and completes the direct format-child set ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L777-L797)).

## Parameter Dimensions

| Dimension | Observed values / source |
|---|---|
| Direct children | Eleven format groups are created from the static `formats` array ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L772-L786)). |
| Nested cases | Each format receives sample-count cases `2`, `4`, `8`, and `16`; sample-count-specific sparse residency features are mapped by `getDeviceCoreFeature()` ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L71-L89), [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L780-L797)). |
| Image shape | All cases use a 2D `256x512x1` image with one mip level and one array layer ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L343-L360), [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L792-L795)). |

## Support / Feature Requirements

Each case requires `sparseBinding`, `sparseResidencyImage2D`, a sample-count-specific sparse residency feature, strict nonresident behavior, supported image size and format, `shaderStorageImageMultisample` for multisample storage images, and `shaderResourceResidency` ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L235-L270)). Runtime setup creates sparse-binding and compute queues, checks sparse support for an image created with `VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT | VK_IMAGE_CREATE_SPARSE_BINDING_BIT`, and rejects images whose memory requirements exceed `sparseAddressSpaceSize` ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L321-L364), [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L372-L390)).

## Verification Methods

The test binds all sparse tiles except the lowest row, dispatches the sparse-image-load shader, copies the result image to a host-visible buffer, and passes only if elements in bound tiles equal the sample count while elements in the unbound row are zero ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L383-L457), [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L559-L621)).

## Test Principles Observed

- The file deliberately leaves one row of sparse image granularity blocks unbound to exercise shader-visible residency status, rather than only testing fully resident sparse images ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L383-L421)).
- Verification combines the SPIR-V/GLSL residency query result with host-side checks for both resident and nonresident regions ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L292-L303), [`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L598-L621)).

## Notes / Uncertainties

- The inspected file registers only the regular `multisampled_image_sparse_residency` root; no device-group variant or nested registered helper file was found in this branch ([`vktSparseResourcesMultisampledImageSparseResidency.cpp`](../../../modules/vulkan/sparse_resources/vktSparseResourcesMultisampledImageSparseResidency.cpp#L806-L809)).
