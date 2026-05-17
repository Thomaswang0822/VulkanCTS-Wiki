# vktYCbCrConversionTests.cpp

## Overview

Comprehensive tests for `VkSamplerYcbcrConversion` color model conversions. Validates that YCbCr-to-RGB color conversion through the sampler produces results within the precision bounds specified by the Vulkan specification. Tests cover all color models, color ranges, chroma locations, chroma filters, component mappings, and explicit/implicit reconstruction modes.

**Role:** Implementation (registers group `ycbcr.conversion`)

**Source:** [vktYCbCrConversionTests.cpp](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp)

## Registration Hierarchy

```text
ycbcr.conversion
├── r4g4b4a4_unorm_pack16
├── b4g4r4a4_unorm_pack16
├── r5g6b5_unorm_pack16
├── b5g6r5_unorm_pack16
├── r5g5b5a1_unorm_pack16
├── b5g5r5a1_unorm_pack16
├── a1r5g5b5_unorm_pack16
├── r8g8b8_unorm
├── b8g8r8_unorm
├── r8g8b8a8_unorm
├── b8g8r8a8_unorm
├── a8b8g8r8_unorm_pack32
├── a2r10g10b10_unorm_pack32
├── a2b10g10r10_unorm_pack32
├── r16g16b16_unorm
├── r16g16b16a16_unorm
├── r10x6_unorm_pack16
├── r10x6g10x6_unorm_2pack16
├── r10x6g10x6b10x6a10x6_unorm_4pack16
├── r12x4_unorm_pack16
├── r12x4g12x4_unorm_2pack16
├── r12x4g12x4b12x4a12x4_unorm_4pack16
├── g8_b8_r8_3plane_444_unorm
├── g10x6_b10x6_r10x6_3plane_444_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_444_unorm_3pack16
├── g16_b16_r16_3plane_444_unorm
├── g8_b8r8_2plane_444_unorm
├── g10x6_b10x6r10x6_2plane_444_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_444_unorm_3pack16
├── g16_b16r16_2plane_444_unorm
├── g8b8g8r8_422_unorm
├── b8g8r8g8_422_unorm
├── g8_b8_r8_3plane_422_unorm
├── g8_b8r8_2plane_422_unorm
├── g10x6b10x6g10x6r10x6_422_unorm_4pack16
├── b10x6g10x6r10x6g10x6_422_unorm_4pack16
├── g10x6_b10x6_r10x6_3plane_422_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_422_unorm_3pack16
├── g12x4b12x4g12x4r12x4_422_unorm_4pack16
├── b12x4g12x4r12x4g12x4_422_unorm_4pack16
├── g12x4_b12x4_r12x4_3plane_422_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_422_unorm_3pack16
├── g16b16g16r16_422_unorm
├── b16g16r16g16_422_unorm
├── g8_b8_r8_3plane_420_unorm
├── g8_b8r8_2plane_420_unorm
├── g10x6_b10x6_r10x6_3plane_420_unorm_3pack16
├── g10x6_b10x6r10x6_2plane_420_unorm_3pack16
├── g12x4_b12x4_r12x4_3plane_420_unorm_3pack16
├── g12x4_b12x4r12x4_2plane_420_unorm_3pack16
├── g16_b16_r16_3plane_420_unorm
├── g16_b16r16_2plane_420_unorm
└── one_to_one
```

## Test Families

### conversion

Verifies that `VkSamplerYcbcrConversion` produces correct color conversion results for all combinations of conversion parameters. The test fills a YCbCr image with channel-specific gradient data, samples it through a shader with the specified conversion configuration, and compares the results against analytically computed precision bounds using `calculateBounds()`.

**Parameter Dimensions:**

| Dimension | Values | Notes |
|-----------|--------|-------|
| Format | All YCbCr formats (`VK_YCBCR_FORMAT_FIRST` through `VK_YCBCR_FORMAT_LAST`, plus 444 EXT formats) | Each format gets its own subgroup |
| Color Model | `VK_SAMPLER_YCBCR_MODEL_CONVERSION_RGB_IDENTITY`, `VK_SAMPLER_YCBCR_MODEL_CONVERSION_YCBCR_IDENTITY`, `VK_SAMPLER_YCBCR_MODEL_CONVERSION_YCBCR_709`, `VK_SAMPLER_YCBCR_MODEL_CONVERSION_YCBCR_601` | Tested individually and as sampler arrays |
| Color Range | `VK_SAMPLER_YCBCR_RANGE_ITU_FULL`, `VK_SAMPLER_YCBCR_RANGE_ITU_NARROW` | Full and narrow range |
| Chroma Filter | `VK_FILTER_NEAREST`, `VK_FILTER_LINEAR` | Chroma sample reconstruction filter |
| Texture Filter | `VK_FILTER_NEAREST`, `VK_FILTER_LINEAR` | Min/mag filter on the sampler |
| Chroma Offset | `VK_CHROMA_LOCATION_MIDPOINT`, `VK_CHROMA_LOCATION_COSITED_EVEN` | X and Y independently |
| Explicit Reconstruction | false, true | Implicit vs. explicit chroma reconstruction |
| Component Mapping | Identity, swapped chroma (R/B swap) | Tests swizzle handling |
| Tiling | optimal, linear | `VK_IMAGE_TILING_OPTIMAL` and `VK_IMAGE_TILING_LINEAR` |
| Disjoint | false, true | `VK_IMAGE_CREATE_DISJOINT_BIT` |
| Sampler Binding | 0, 1 | Tests non-zero binding for sampler arrays |

**Support Requirements:**

- `VK_KHR_sampler_ycbcr_conversion` extension and `samplerYcbcrConversion` feature
- `VK_FORMAT_FEATURE_MIDPOINT_CHROMA_SAMPLES_BIT` or `VK_FORMAT_FEATURE_COSITED_CHROMA_SAMPLES_BIT`
- `VK_FORMAT_FEATURE_SAMPLED_IMAGE_BIT`
- `VK_FORMAT_FEATURE_SAMPLED_IMAGE_FILTER_LINEAR_BIT` for linear texture filtering
- `VK_FORMAT_FEATURE_SAMPLED_IMAGE_YCBCR_CONVERSION_LINEAR_FILTER_BIT` for linear chroma filtering
- `VK_FORMAT_FEATURE_SAMPLED_IMAGE_YCBCR_CONVERSION_SEPARATE_RECONSTRUCTION_FILTER_BIT` for different chroma/texture filters
- `VK_FORMAT_FEATURE_SAMPLED_IMAGE_YCBCR_CONVERSION_CHROMA_RECONSTRUCTION_EXPLICIT_FORCEABLE_BIT` for explicit reconstruction
- `VK_FORMAT_FEATURE_DISJOINT_BIT` for disjoint images

**Verification Method:**

Uses `calculateBounds()` from `vktYCbCrUtil` to compute per-pixel min/max bounds based on the Vulkan YCbCr conversion precision specification. The shader results are compared against these bounds. For implicit nearest with cosited chroma, both cosited and midpoint bounds are computed and the result must fall within at least one set of bounds. Results are logged with detailed UV/IJ bounds and luma/chroma values on failure.

**Key Functions:**

- [textureConversionTest()](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L650) - Main test implementation
- [evalShader()](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L399) - Shader execution with conversion parameters
- [YCbCrConversionTestBuilder::buildTests()](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp) - Test case generation with all parameter combinations
- [createConversionTests()](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L2192) - Factory function returning the `conversion` group
