# vktYCbCrImageQueryTests.cpp

## Overview

Tests SPIR-V image query operations (`OpImageQuerySizeLod` and `OpImageQueryLevels`) on YCbCr multi-planar images. Verifies that the reported image dimensions and level counts are correct when a YCbCr image is accessed through a combined image sampler with a `VkSamplerYcbcrConversion`.

**Role:** Implementation (registers group `ycbcr.query`)

**Source:** [vktYCbCrImageQueryTests.cpp](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp)

## Registration Hierarchy

```text
ycbcr.query
├── size_lod
└── levels
```

## Test Families

### query

Verifies that `OpImageQuerySizeLod` and `OpImageQueryLevels` return correct values for YCbCr images. For `size_lod`, the test creates images at multiple sizes (aligned to the format's maximum plane divisor) and verifies the returned dimensions match. For `levels`, the test verifies the returned level count is 1.

**Query Types:**

| Query Type | SPIR-V Op | GLSL Expression | Expected Result |
|------------|-----------|-----------------|-----------------|
| `size_lod` | `OpImageQuerySizeLod` | `textureSize(u_image, lod)` | Image width and height |
| `levels` | `OpImageQueryLevels` | `textureQueryLevels(u_image)` | 1 (single mip level) |

**Parameter Dimensions:**

| Dimension | Values | Notes |
|-----------|--------|-------|
| Query Type | `QUERY_TYPE_IMAGE_SIZE_LOD`, `QUERY_TYPE_IMAGE_LEVELS` | Size query vs. level count query |
| Format | `VK_FORMAT_R8G8B8A8_UNORM` (reference), all YCbCr formats (`VK_YCBCR_FORMAT_FIRST` through `VK_YCBCR_FORMAT_LAST`, plus 444 EXT formats) | Non-YCbCr reference included |
| Disjoint | false, true | `VK_IMAGE_CREATE_DISJOINT_BIT` (multi-plane formats only) |
| Shader Type | All supported shader stages | vertex, fragment, geometry, tessellation_control, tessellation_evaluation, compute (filtered by `executorSupported()`) |

**Support Requirements:**

- `VK_FORMAT_FEATURE_MIDPOINT_CHROMA_SAMPLES_BIT` for YCbCr formats
- Shader stage support via `checkSupportShader()`

**Verification Method:**

For `size_lod`: Creates images at 6 different sizes (multiples of the format's max plane divisor: 1x, 2x1, 1x2, 63x79, 99x1, 421x1117), samples each with `textureSize()`, and compares the returned `ivec2` against the known image dimensions.

For `levels`: Creates a single image and verifies `textureQueryLevels()` returns 1.

**Key Functions:**

- [testImageQuery()](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L330) - Main test implementation
- [populateQueryGroup()](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L579) - Per-query-type group population
- [populateImageQueryGroup()](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L593) - Top-level query group population
- [createImageQueryTests()](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L603) - Factory function returning the `query` group
