# vktYCbCrConversionTests.cpp

## Overview

[`vktYCbCrConversionTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp) implements the `ycbcr.conversion` subgroup returned by [`createConversionTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L2192-L2195). It verifies sampler YCbCr conversion by filling channel gradients, sampling through one or more `VkSamplerYcbcrConversion` objects, and checking shader output against precision bounds in [`textureConversionTest()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L650-L815).

## Registration Hierarchy

```text
ycbcr.conversion
├── a1r5g5b5_unorm_pack16
├── a2b10g10r10_unorm_pack32
├── a2r10g10b10_unorm_pack32
├── a8b8g8r8_unorm_pack32
├── b10x6g10x6r10x6g10x6_422_unorm_4pack16
├── b12x4g12x4r12x4g12x4_422_unorm_4pack16
├── b16g16r16g16_422_unorm
├── b4g4r4a4_unorm_pack16
├── b5g5r5a1_unorm_pack16
├── b5g6r5_unorm_pack16
├── b8g8r8_unorm
├── b8g8r8a8_unorm
├── b8g8r8g8_422_unorm
├── g10x6_b10x6_r10x6_3plane_420_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_422_unorm_3pack16
├── g10x6_b10x6_r10x6_3plane_444_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_420_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_422_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_444_unorm_3pack16
├── g10x6b10x6g10x6r10x6_422_unorm_4pack16
├── g12x4_b12x4_r12x4_3plane_420_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_422_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_444_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_420_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_422_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_444_unorm_3pack16
├── g12x4b12x4g12x4r12x4_422_unorm_4pack16
├── g16_b16_r16_3plane_420_unorm
├── g16_b16_r16_3plane_422_unorm
├── g16_b16_r16_3plane_444_unorm
├── g16_b16r16_2plane_420_unorm
├── g16_b16r16_2plane_422_unorm
├── g16_b16r16_2plane_444_unorm
├── g16b16g16r16_422_unorm
├── g8_b8_r8_3plane_420_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8_r8_3plane_444_unorm
├── g8_b8r8_2plane_420_unorm
├── g8_b8r8_2plane_422_unorm
├── g8_b8r8_2plane_444_unorm
├── g8b8g8r8_422_unorm
├── one_to_one
├── r10x6_unorm_pack16
├── r10x6g10x6_unorm_2pack16
├── r10x6g10x6b10x6a10x6_unorm_4pack16
├── r12x4_unorm_pack16
├── r12x4g12x4_unorm_2pack16
├── r12x4g12x4b12x4a12x4_unorm_4pack16
├── r16g16b16_unorm
├── r16g16b16a16_unorm
├── r4g4b4a4_unorm_pack16
├── r5g5b5a1_unorm_pack16
├── r5g6b5_unorm_pack16
├── r8g8b8_unorm
└── r8g8b8a8_unorm
```

[`initTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L2184-L2188) delegates generation to [`YCbCrConversionTestBuilder::buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1362-L2180). The direct children are format groups plus `one_to_one`; format groups are created from source-derived format names, while deeper `color_conversion`, `chroma_reconstruction`, and `sampler_array` descendants are described under Test Families.

## Test Families

### conversion

Color conversion cases vary color model, range, tiling, texture filter, chroma location, shader stage, and sampler binding for non-subsampled formats in [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1367-L1490), X-subsampled formats in [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1493-L1608), and XY-subsampled formats in [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1799-L1908).

### chroma_reconstruction

For subsampled formats, chroma reconstruction cases vary texture filter, explicit reconstruction, disjoint state, chroma offsets, tiling, and identity/swapped-chroma component mapping in [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1610-L1794) and [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1910-L2089).

### one_to_one and sampler_array

The `one_to_one` group uses `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM`, two image sizes, both chroma-offset axes, and both tilings in [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L2092-L2138). Sampler-array cases use `VK_SAMPLER_YCBCR_MODEL_CONVERSION_LAST` as a sentinel and create an array of up to the first four model conversions in [`buildArrayOfSamplersTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L2141-L2180) and [`textureConversionTest()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L779-L792).

## Parameters

| Dimension | Source-backed values |
|---|---|
| Color models | RGB identity, YCbCr identity, BT.709, BT.601, and BT.2020 are selected from the builder's `colorModels` loops; non-RGB models are skipped for formats with fewer than three YCbCr channels in [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1375-L1382). |
| Color range | Full and narrow ranges are generated, but narrow range is skipped when any YCbCr bit depth is below 8 bits in [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1432-L1439), [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1560-L1567), and [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1863-L1870). |
| Filters and offsets | Texture filters, chroma filters, and midpoint/cosited chroma offsets feed `TestConfig` construction throughout [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1538-L1549) and [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1949-L1963). |
| Tiling/disjoint | Optimal/linear tiling and disjoint variants are generated in chroma-reconstruction loops in [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1627-L1661) and [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1927-L1963). |
| Sampler binding | Binding `0` and nonzero sampler bindings are included via `samplerBindings` loops, for example in [`buildTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1404-L1420). |

## Support Requirements

[`checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L526-L645) checks image-format support, plane-compatible support for disjoint images, `VK_KHR_sampler_ycbcr_conversion`, the `samplerYcbcrConversion` feature, sampled-image support, linear texture filtering, linear chroma filtering, separate reconstruction filtering, explicit reconstruction forceability, disjoint support, and midpoint/cosited chroma-sample support as required by each `TestConfig`.

## Verification Method

[`textureConversionTest()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L650-L815) fills R/G/B/A channel gradients, chooses generated texture coordinates, runs shader sampling via [`evalShader()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L399-L482), computes per-pixel bounds with [`calculateBounds()`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L1625), and for implicit-nearest cosited chroma also computes midpoint bounds so a result may satisfy either bound set.

## Notes / Uncertainties

The source includes `FAKE_COLOR_CONVERSION` preprocessor branches; this documentation describes the normal non-fake support and verification path visible in the inspected source.
