# vktYCbCrFilteringTests.cpp

## Overview

Tests YCbCr image linear filtering with chroma reconstruction. Validates that sampling a YCbCr image with a linear sampler and various chroma filters produces results within calculated precision bounds. Tests run in both graphics (fragment shader) and compute pipelines.

**Role:** Implementation (registers group `ycbcr.filtering`)

**Source:** [vktYCbCrFilteringTests.cpp](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp)

## Registration Hierarchy

```text
ycbcr.filtering
├── linear_sampler_g8_b8_r8_3plane_420_unorm_graphics
├── linear_sampler_with_chroma_linear_filtering_g8_b8_r8_3plane_420_unorm_graphics
├── linear_sampler_g8_b8_r8_3plane_420_unorm_compute
├── linear_sampler_with_chroma_linear_filtering_g8_b8_r8_3plane_420_unorm_compute
├── linear_sampler_g8_b8r8_2plane_420_unorm_graphics
├── linear_sampler_with_chroma_linear_filtering_g8_b8r8_2plane_420_unorm_graphics
├── linear_sampler_g8_b8r8_2plane_420_unorm_compute
├── linear_sampler_with_chroma_linear_filtering_g8_b8r8_2plane_420_unorm_compute
├── linear_sampler_g10_b10_r10_3plane_420_unorm_3pack16_graphics
├── linear_sampler_with_chroma_linear_filtering_g10_b10_r10_3plane_420_unorm_3pack16_graphics
├── linear_sampler_g10_b10_r10_3plane_420_unorm_3pack16_compute
├── linear_sampler_with_chroma_linear_filtering_g10_b10_r10_3plane_420_unorm_3pack16_compute
├── linear_sampler_g10_b10r10_2plane_420_unorm_3pack16_graphics
├── linear_sampler_with_chroma_linear_filtering_g10_b10r10_2plane_420_unorm_3pack16_graphics
├── linear_sampler_g10_b10r10_2plane_420_unorm_3pack16_compute
├── linear_sampler_with_chroma_linear_filtering_g10_b10r10_2plane_420_unorm_3pack16_compute
├── linear_sampler_g12_b12_r12_3plane_420_unorm_3pack16_graphics
├── linear_sampler_with_chroma_linear_filtering_g12_b12_r12_3plane_420_unorm_3pack16_graphics
├── linear_sampler_g12_b12_r12_3plane_420_unorm_3pack16_compute
├── linear_sampler_with_chroma_linear_filtering_g12_b12_r12_3plane_420_unorm_3pack16_compute
├── linear_sampler_g12_b12r12_2plane_420_unorm_3pack16_graphics
├── linear_sampler_with_chroma_linear_filtering_g12_b12r12_2plane_420_unorm_3pack16_graphics
├── linear_sampler_g12_b12r12_2plane_420_unorm_3pack16_compute
├── linear_sampler_with_chroma_linear_filtering_g12_b12r12_2plane_420_unorm_3pack16_compute
├── linear_sampler_g16_b16_r16_3plane_420_unorm_graphics
├── linear_sampler_with_chroma_linear_filtering_g16_b16_r16_3plane_420_unorm_graphics
├── linear_sampler_g16_b16_r16_3plane_420_unorm_compute
├── linear_sampler_with_chroma_linear_filtering_g16_b16_r16_3plane_420_unorm_compute
├── linear_sampler_g16_b16r16_2plane_420_unorm_graphics
├── linear_sampler_with_chroma_linear_filtering_g16_b16r16_2plane_420_unorm_graphics
├── linear_sampler_g16_b16r16_2plane_420_unorm_compute
└── linear_sampler_with_chroma_linear_filtering_g16_b16r16_2plane_420_unorm_compute
```

## Test Families

### filtering

Verifies that YCbCr linear filtering with chroma reconstruction produces results within the precision bounds defined by the Vulkan specification. The test renders a full-screen quad (graphics) or dispatches a compute shader that samples the YCbCr image, then compares results against analytically computed min/max bounds using `calculateBounds()`.

**Parameter Dimensions:**

| Dimension | Values | Notes |
|-----------|--------|-------|
| Format | `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM`, `VK_FORMAT_G8_B8R8_2PLANE_420_UNORM`, `VK_FORMAT_G10X6_B10X6_R10X6_3PLANE_420_UNORM_3PACK16`, `VK_FORMAT_G10X6_B10X6R10X6_2PLANE_420_UNORM_3PACK16`, `VK_FORMAT_G12X4_B12X4_R12X4_3PLANE_420_UNORM_3PACK16`, `VK_FORMAT_G12X4_B12X4R12X4_2PLANE_420_UNORM_3PACK16`, `VK_FORMAT_G16_B16_R16_3PLANE_420_UNORM`, `VK_FORMAT_G16_B16R16_2PLANE_420_UNORM` | 420 subsampling formats (8/10/12/16-bit, 2-plane and 3-plane) |
| Chroma Filter | `VK_FILTER_NEAREST`, `VK_FILTER_LINEAR` | Nearest = no chroma interpolation; Linear = chroma interpolation |
| Pipeline | graphics, compute | Fragment shader rendering vs. compute dispatch |

**Support Requirements:**

- `VK_KHR_sampler_ycbcr_conversion` extension and `samplerYcbcrConversion` feature
- `VK_FORMAT_FEATURE_MIDPOINT_CHROMA_SAMPLES_BIT` for the format
- `VK_FORMAT_FEATURE_SAMPLED_IMAGE_FILTER_LINEAR_BIT` for linear filtering
- `VK_FORMAT_FEATURE_SAMPLED_IMAGE_YCBCR_CONVERSION_LINEAR_FILTER_BIT` for linear chroma filtering
- `VK_FORMAT_FEATURE_SAMPLED_IMAGE_YCBCR_CONVERSION_SEPARATE_RECONSTRUCTION_FILTER_BIT` when chroma filter differs from texture filter

**Verification Method:**

Uses `calculateBounds()` from `vktYCbCrUtil` to compute per-pixel min/max bounds based on the Vulkan precision requirements for YCbCr conversion. The rendered/computed result image is compared against these bounds. Any pixel outside the bounds is a failure. The test uses two image/render size pairs: `{8,8}/{64,64}` and `{64,32}/{32,64}`.

**Key Classes and Functions:**

- [LinearFilteringTestInstance](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L334) - Graphics pipeline test instance
- [LinearFilteringComputeTestInstance](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L490) - Compute pipeline test instance
- [LinearFilteringTestCase](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L678) - Test case with support checking
- [verifyFilteringResult()](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L206) - Shared verification logic
- [createFilteringTests()](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L787) - Factory function returning the `filtering` group
