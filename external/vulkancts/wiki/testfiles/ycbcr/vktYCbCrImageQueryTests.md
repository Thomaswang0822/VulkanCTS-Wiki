# vktYCbCrImageQueryTests.cpp

## Overview

[`vktYCbCrImageQueryTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp) implements the `ycbcr.query` subgroup returned by [`createImageQueryTests()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L603-L605). It tests `OpImageQuerySizeLod` and `OpImageQueryLevels` through GLSL texture-query expressions generated for executor-supported shader stages in [`populateImageQueryGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L593-L599) and [`populateQueryGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L579-L590).

## Registration Hierarchy

```text
ycbcr.query
├── size_lod
└── levels
```

`size_lod` and `levels` are added by [`populateImageQueryGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L593-L599); each query type creates shader-stage groups and then adds a non-YCbCr reference format plus YCbCr formats and disjoint variants in [`populateQueryInShaderGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L548-L577).

## Test Families

### size_lod

`size_lod` cases compare the shader-returned `UVec2` against constructed image dimensions in [`testImageQuery()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L418-L465).

### levels

`levels` cases use the same test path to check the expected single mip level for the constructed image in [`testImageQuery()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L437-L465).

## Parameters

| Dimension | Source-backed values |
|---|---|
| Query type | `QUERY_TYPE_IMAGE_SIZE_LOD` and `QUERY_TYPE_IMAGE_LEVELS` are registered as `size_lod` and `levels` in [`populateImageQueryGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L593-L599). |
| Formats | `VK_FORMAT_R8G8B8A8_UNORM` is added as a reference, then YCbCr base and 444 EXT ranges are added in [`populateQueryInShaderGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L550-L576). |
| Disjoint | Disjoint variants are generated when `getPlaneCount(format) > 1` in [`populateQueryInShaderGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L559-L575). |
| Image sizes | `size_lod` tests six sizes derived from the format's maximum plane divisor; `levels` uses one `16x18` image in [`testImageQuery()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L418-L439). |
| Shader type | Executor-supported shader stages are filtered by `executorSupported()` in [`populateQueryGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L581-L589). |

## Support Requirements

[`checkSupport()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L495-L515) applies shared YCbCr image support only to YCbCr formats, then requires midpoint chroma-sample support for YCbCr formats and checks shader-stage support.

## Verification Method

For `size_lod`, [`testImageQuery()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L418-L465) compares the shader-returned `UVec2` against each constructed image size. For `levels`, the same switch path checks the expected single mip level for the one constructed image; image construction uses one mip level in `TestImage` creation through [`testImageQuery()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L437-L439).

## Notes / Uncertainties

The reference `VK_FORMAT_R8G8B8A8_UNORM` cases are intentionally included by the generator and are not YCbCr conversion cases.
