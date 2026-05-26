# vktYCbCrFilteringTests.cpp

## Overview

[`vktYCbCrFilteringTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp) implements the `ycbcr.filtering` subgroup returned by [`createFilteringTests()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L787-L807). It registers graphics and compute cases that sample 4:2:0 YCbCr images with linear texture filtering and either nearest or linear chroma filtering in [`createFilteringTests()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L795-L835).

## Registration Hierarchy

```text
ycbcr.filtering
├── linear_sampler_g10_b10_r10_3plane_420_unorm_3pack16_compute
├── linear_sampler_g10_b10_r10_3plane_420_unorm_3pack16_graphics
├── linear_sampler_g10_b10r10_2plane_420_unorm_3pack16_compute
├── linear_sampler_g10_b10r10_2plane_420_unorm_3pack16_graphics
├── linear_sampler_g12_b12_r12_3plane_420_unorm_3pack16_compute
├── linear_sampler_g12_b12_r12_3plane_420_unorm_3pack16_graphics
├── linear_sampler_g12_b12r12_2plane_420_unorm_3pack16_compute
├── linear_sampler_g12_b12r12_2plane_420_unorm_3pack16_graphics
├── linear_sampler_g16_b16_r16_3plane_420_unorm_compute
├── linear_sampler_g16_b16_r16_3plane_420_unorm_graphics
├── linear_sampler_g16_b16r16_2plane_420_unorm_compute
├── linear_sampler_g16_b16r16_2plane_420_unorm_graphics
├── linear_sampler_g8_b8_r8_3plane_420_unorm_compute
├── linear_sampler_g8_b8_r8_3plane_420_unorm_graphics
├── linear_sampler_g8_b8r8_2plane_420_unorm_compute
├── linear_sampler_g8_b8r8_2plane_420_unorm_graphics
├── linear_sampler_with_chroma_linear_filtering_g10_b10_r10_3plane_420_unorm_3pack16_compute
├── linear_sampler_with_chroma_linear_filtering_g10_b10_r10_3plane_420_unorm_3pack16_graphics
├── linear_sampler_with_chroma_linear_filtering_g10_b10r10_2plane_420_unorm_3pack16_compute
├── linear_sampler_with_chroma_linear_filtering_g10_b10r10_2plane_420_unorm_3pack16_graphics
├── linear_sampler_with_chroma_linear_filtering_g12_b12_r12_3plane_420_unorm_3pack16_compute
├── linear_sampler_with_chroma_linear_filtering_g12_b12_r12_3plane_420_unorm_3pack16_graphics
├── linear_sampler_with_chroma_linear_filtering_g12_b12r12_2plane_420_unorm_3pack16_compute
├── linear_sampler_with_chroma_linear_filtering_g12_b12r12_2plane_420_unorm_3pack16_graphics
├── linear_sampler_with_chroma_linear_filtering_g16_b16_r16_3plane_420_unorm_compute
├── linear_sampler_with_chroma_linear_filtering_g16_b16_r16_3plane_420_unorm_graphics
├── linear_sampler_with_chroma_linear_filtering_g16_b16r16_2plane_420_unorm_compute
├── linear_sampler_with_chroma_linear_filtering_g16_b16r16_2plane_420_unorm_graphics
├── linear_sampler_with_chroma_linear_filtering_g8_b8_r8_3plane_420_unorm_compute
├── linear_sampler_with_chroma_linear_filtering_g8_b8_r8_3plane_420_unorm_graphics
├── linear_sampler_with_chroma_linear_filtering_g8_b8r8_2plane_420_unorm_compute
└── linear_sampler_with_chroma_linear_filtering_g8_b8r8_2plane_420_unorm_graphics
```

The direct children are generated per 4:2:0 format, chroma-filter mode, and graphics/compute execution path in [`createFilteringTests()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L795-L835).

## Test Families

### filtering

The graphics path renders sampled values with a fragment shader in [`LinearFilteringTestInstance::iterate()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L389-L481), while the compute path writes sampled values to an output image in [`LinearFilteringComputeTestInstance::iterate()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L526-L669). Both paths call [`verifyFilteringResult()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L206-L265) for precision-bounded validation.

## Parameters

| Dimension | Source-backed values |
|---|---|
| Formats | Eight 4:2:0 2-plane/3-plane formats at 8/10/12/16 bits are listed in `ycbcrFormats` in [`createFilteringTests()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L795-L804). |
| Chroma filter | Each format gets a nearest-chroma case and a linear-chroma case via `VK_FILTER_NEAREST` and `VK_FILTER_LINEAR` constructor arguments in [`createFilteringTests()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L811-L834). |
| Pipeline | Graphics cases use `LinearFilteringTestInstance`; compute cases pass `false` for `m_useGraphics` and create `LinearFilteringComputeTestInstance` in [`LinearFilteringTestCase::createInstance()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L732-L738). |
| Image/render sizes | Verification is invoked with `{8,8}->{64,64}` and `{64,32}->{32,64}` size pairs in the graphics and compute paths, as shown by the calls to [`verifyFilteringResult()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L481) and [`verifyFilteringResult()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L669). |

## Support Requirements

[`LinearFilteringTestCase::checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L704-L730) requires `VK_KHR_sampler_ycbcr_conversion`, the `samplerYcbcrConversion` feature, midpoint chroma samples, linear texture filtering, separate reconstruction filtering when chroma and texture filters differ, and YCbCr linear chroma filtering for `VK_FILTER_LINEAR` chroma cases.

## Verification Method

[`verifyFilteringResult()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L206-L265) computes expected min/max bounds with [`calculateBounds()`](../../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L1625) and fails any pixel outside those bounds; the shader programs sampled by the cases are generated in [`LinearFilteringTestCase::initPrograms()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L740-L783).

## Notes / Uncertainties

The file focuses on the eight explicit 4:2:0 formats in the local `ycbcrFormats` vector; it does not iterate the full YCbCr format range in this subgroup.
