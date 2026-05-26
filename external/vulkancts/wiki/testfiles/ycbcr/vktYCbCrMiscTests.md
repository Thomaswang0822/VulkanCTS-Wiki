# vktYCbCrMiscTests.cpp

## Overview

[`vktYCbCrMiscTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp) implements the `ycbcr.misc` subgroup returned by [`createMiscTests()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L366-L370). The current source registers a single `relaxed_precision` case.

## Registration Hierarchy

```text
ycbcr.misc
└── relaxed_precision
```

The single child is added by [`createMiscTests()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L366-L370).

## Test Families

### relaxed_precision

The current miscellaneous family contains only `relaxed_precision`, which is implemented by [`RelaxedPrecisionTestCase`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L278-L291) and [`RelaxedPrecisionTestInstance`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L60-L270).

The test uses `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM`, a `256x256` render target, RGB identity/full-range YCbCr conversion, cosited chroma locations, and nearest filtering in [`RelaxedPrecisionTestInstance::iterate()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L68-L89). Its fragment shader is handwritten SPIR-V assembly with `RelaxedPrecision` decorations on the output, sampler variable, sampled values, and intermediate multiplication; it samples with `OpImageSampleImplicitLod` and `OpImageSampleProjImplicitLod` in [`RelaxedPrecisionTestCase::initPrograms()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L310-L364).

## Parameters

| Dimension | Source-backed values |
|---|---|
| Format | `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM` in [`iterate()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L68-L75). |
| Render size | `256x256` in [`iterate()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L68-L69). |
| Conversion | RGB identity, ITU full range, cosited-even chroma locations, nearest chroma filter in [`iterate()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L71-L87). |
| SPIR-V operations | `OpImageSampleImplicitLod`, `OpImageSampleProjImplicitLod`, and `OpFMul` in [`initPrograms()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L352-L358). |

## Support Requirements

[`RelaxedPrecisionTestCase::checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L294-L297) requires `VK_KHR_sampler_ycbcr_conversion`.

## Verification Method

The test records and submits a draw using the generated graphics pipeline in [`RelaxedPrecisionTestInstance::iterate()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L241-L270). There is no source-visible pixel comparison in this file; the test's pass condition is successful pipeline execution of the relaxed-precision YCbCr sampler operations.

## Notes / Uncertainties

The source currently contains no additional `misc` children beyond `relaxed_precision` in [`createMiscTests()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L366-L370).
