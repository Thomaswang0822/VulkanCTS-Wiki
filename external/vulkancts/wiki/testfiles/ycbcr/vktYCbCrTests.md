# vktYCbCrTests.cpp

## Overview

This is the **registration file** for the YCbCr test category. It serves as the top-level entry point that aggregates all YCbCr-related test groups into a single `ycbcr` test tree. The file contains no test logic itself; it delegates to individual implementation files via their respective `create*Tests()` factory functions.

**Role:** Registration only

**Source:** [vktYCbCrTests.cpp](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp)

## Registration Hierarchy

```text
ycbcr
├── format
├── filtering
├── plane_view
├── query
├── conversion
├── copy
├── single_plane_copy
├── copy_dimensions
├── storage_image_write
├── subresource_offset
└── misc
```

## Test Families

| Group | Factory Function | Implementation File | Description |
|-------|-----------------|---------------------|-------------|
| `format` | `createFormatTests()` | vktYCbCrFormatTests.cpp | YCbCr format sampling tests across all multi-planar formats |
| `filtering` | `createFilteringTests()` | vktYCbCrFilteringTests.cpp | YCbCr linear filtering with chroma reconstruction |
| `plane_view` | `createViewTests()` | vktYCbCrViewTests.cpp | Plane-level image view access of multi-planar images |
| `query` | `createImageQueryTests()` | vktYCbCrImageQueryTests.cpp | OpImageQuerySizeLod and OpImageQueryLevels on YCbCr images |
| `conversion` | `createConversionTests()` | vktYCbCrConversionTests.cpp | Sampler YCbCr color model conversion tests |
| `copy` | `createCopyTests()` | vktYCbCrCopyTests.cpp | Image-to-image copy between YCbCr and compatible formats |
| `single_plane_copy` | `createSinglePlanarCopyTests()` | vktYCbCrCopyTests.cpp | Single-planar format copy to/from YCbCr 422 formats |
| `copy_dimensions` | `createDimensionsCopyTests()` | vktYCbCrCopyTests.cpp | YCbCr copy tests with extreme image dimensions |
| `storage_image_write` | `createStorageImageWriteTests()` | vktYCbCrStorageImageWriteTests.cpp | Compute shader writing to multi-planar storage images |
| `subresource_offset` | `createImageOffsetTests()` | vktYCbCrImageOffsetTests.cpp | VkSubresourceLayout offset validation for disjoint YCbCr images |
| `misc` | `createMiscTests()` | vktYCbCrMiscTests.cpp | Miscellaneous YCbCr tests (relaxed precision) |

## Registration Code

The `populateTestGroup()` function at [vktYCbCrTests.cpp#L44](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L44) adds all child groups. The public entry point `createTests()` at [vktYCbCrTests.cpp#L63](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L63) wraps this into a `tcu::TestCaseGroup`.
