# vktYCbCrMiscTests.cpp

## Overview

Miscellaneous YCbCr tests that do not fit into other categories. Currently contains a single test for relaxed precision decoration handling with YCbCr samplers.

**Role:** Implementation (registers group `ycbcr.misc`)

**Source:** [vktYCbCrMiscTests.cpp](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp)

## Registration Hierarchy

```text
ycbcr.misc
└── relaxed_precision
```

## Test Families

### misc

Contains miscellaneous YCbCr-related tests. The current test validates that `RelaxedPrecision` decorations in SPIR-V work correctly with YCbCr sampler operations.

#### relaxed_precision

Tests that a fragment shader with `RelaxedPrecision` decorations on YCbCr sampler operations (`OpImageSampleImplicitLod` and `OpImageSampleProjImplicitLod`) executes without errors. The test uses a hand-crafted SPIR-V assembly fragment shader that:

1. Samples a YCbCr image at coordinates (0,0) via `OpImageSampleImplicitLod`
2. Samples the same image with projective sampling via `OpImageSampleProjImplicitLod`
3. Multiplies the two results and stores to the output

The `RelaxedPrecision` decoration is applied to the sampler variable, the sampled results, and intermediate computations. The test verifies that the pipeline compiles and executes successfully without crashes or validation errors.

**Parameter Dimensions:**

| Dimension | Values | Notes |
|-----------|--------|-------|
| Format | `VK_FORMAT_G8_B8_R8_3PLANE_420_UNORM` | Fixed format for this test |
| Render Size | 256x256 | Fixed |
| Chroma Location | `VK_CHROMA_LOCATION_COSITED_EVEN` (both X and Y) | Fixed |
| Color Model | `VK_SAMPLER_YCBCR_MODEL_CONVERSION_RGB_IDENTITY` | Fixed |
| Color Range | `VK_SAMPLER_YCBCR_RANGE_ITU_FULL` | Fixed |

**Support Requirements:**

- `VK_KHR_sampler_ycbcr_conversion` extension

**Verification Method:**

The test passes if the graphics pipeline executes without errors. No pixel-level result verification is performed; the test validates that the SPIR-V with `RelaxedPrecision` decorations on YCbCr sampler operations is accepted by the driver and does not cause crashes or validation errors.

**Key Classes and Functions:**

- [RelaxedPrecisionTestInstance](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L49) - Test instance implementation
- [RelaxedPrecisionTestCase](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L278) - Test case with SPIR-V assembly fragment shader
- [createMiscTests()](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L366) - Factory function returning the `misc` group
