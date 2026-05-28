# vktYCbCrTests.cpp

## Overview

[`vktYCbCrTests.cpp`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp) is the registration-only file for the top-level `ycbcr` category: [`createTests()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L63-L65) wraps [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L44-L58), and `populateTestGroup()` adds all child groups without implementing test logic itself.

**Role:** Registration only, with test behavior delegated to the implementation factories linked below.

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

| Group | Factory function | Evidence-backed role |
|---|---|---|
| `format` | [`createFormatTests()`](../../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L734-L737) | Added by [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L48) to cover generated format sampling cases. |
| `filtering` | [`createFilteringTests()`](../../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L787-L835) | Added by [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L49) to cover graphics/compute filtering cases. |
| `plane_view` | [`createViewTests()`](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1075-L1078) | Added by [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L50) to cover image-view and memory-alias plane access. |
| `query` | [`createImageQueryTests()`](../../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L603-L605) | Added by [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L51) to cover `size_lod` and `levels` image queries. |
| `conversion` | [`createConversionTests()`](../../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L2192-L2195) | Added by [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L52) to cover sampler YCbCr conversion matrices. |
| `copy` | [`createCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1023-L1026) | Added by [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L53) for default image-copy cases. |
| `single_plane_copy` | [`createSinglePlanarCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1028-L1031) | Added by [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L54) for 422 single-planar copy pairs. |
| `copy_dimensions` | [`createDimensionsCopyTests()`](../../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1033-L1036) | Added by [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L55) for wide/tall copy dimensions. |
| `storage_image_write` | [`createStorageImageWriteTests()`](../../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L939-L942) | Added by [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L56) for compute storage-image writes. |
| `subresource_offset` | [`createImageOffsetTests()`](../../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L167-L170) | Added by [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L57) for disjoint plane layout offsets. |
| `misc` | [`createMiscTests()`](../../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L366-L370) | Added by [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L58) for the current relaxed-precision case. |

## Support / Feature Requirements

This file does not perform support checks itself; support gating is in each implementation factory's test cases, while this file only wires child groups through [`populateTestGroup()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L44-L58).

## Verification Methods

This file has no verification logic; it returns a populated `tcu::TestCaseGroup` from [`createTests()`](../../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L63-L65).
