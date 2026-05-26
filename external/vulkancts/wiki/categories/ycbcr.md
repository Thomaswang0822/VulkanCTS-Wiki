# ycbcr

## Overview

The [`ycbcr`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L63-L65) category is the Vulkan CTS entry point for sampler YCbCr conversion, multi-planar format, copy, plane-view, query, storage-write, subresource-layout, and miscellaneous YCbCr tests registered by [`populateTestGroup()`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L44-L58). The category is source-driven: each child is added by a `create*Tests()` factory in the top-level registration file rather than by this wiki page.

## Registration Entry Point

[`createTests()`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L63-L65) returns a `tcu::TestCaseGroup` populated by [`populateTestGroup()`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L44-L58). The inspected registration order is:

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

## File Inventory

| File | Registered role | Source evidence |
|---|---|---|
| [`vktYCbCrTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp) | Top-level category registration | [`populateTestGroup()`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp#L44-L58) |
| [`vktYCbCrFormatTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp) | `format` subgroup | [`createFormatTests()`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L734-L737) |
| [`vktYCbCrFilteringTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp) | `filtering` subgroup | [`createFilteringTests()`](../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L787-L807) |
| [`vktYCbCrViewTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp) | `plane_view` subgroup | [`createViewTests()`](../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1075-L1078) |
| [`vktYCbCrImageQueryTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp) | `query` subgroup | [`createImageQueryTests()`](../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L603-L605) |
| [`vktYCbCrConversionTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp) | `conversion` subgroup | [`createConversionTests()`](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L2192-L2195) |
| [`vktYCbCrCopyTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp) | `copy`, `single_plane_copy`, and `copy_dimensions` subgroups | [`createCopyTests()` family](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1023-L1036) |
| [`vktYCbCrStorageImageWriteTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp) | `storage_image_write` subgroup | [`createStorageImageWriteTests()`](../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L939-L942) |
| [`vktYCbCrImageOffsetTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp) | `subresource_offset` subgroup | [`createImageOffsetTests()`](../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L167-L170) |
| [`vktYCbCrMiscTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp) | `misc` subgroup | [`createMiscTests()`](../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L366-L370) |
| [`vktYCbCrUtil.cpp`](../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp) | Shared image, memory, upload, and precision helpers | [`checkImageSupport()`](../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L176-L201), [`calculateBounds()`](../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L1625) |

## Level-3 Documents

| Source file | Wiki document |
|---|---|
| [`vktYCbCrTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrTests.cpp) | [`vktYCbCrTests.md`](../testfiles/ycbcr/vktYCbCrTests.md) |
| [`vktYCbCrFormatTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp) | [`vktYCbCrFormatTests.md`](../testfiles/ycbcr/vktYCbCrFormatTests.md) |
| [`vktYCbCrFilteringTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp) | [`vktYCbCrFilteringTests.md`](../testfiles/ycbcr/vktYCbCrFilteringTests.md) |
| [`vktYCbCrViewTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp) | [`vktYCbCrViewTests.md`](../testfiles/ycbcr/vktYCbCrViewTests.md) |
| [`vktYCbCrImageQueryTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp) | [`vktYCbCrImageQueryTests.md`](../testfiles/ycbcr/vktYCbCrImageQueryTests.md) |
| [`vktYCbCrConversionTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp) | [`vktYCbCrConversionTests.md`](../testfiles/ycbcr/vktYCbCrConversionTests.md) |
| [`vktYCbCrCopyTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp) | [`vktYCbCrCopyTests.md`](../testfiles/ycbcr/vktYCbCrCopyTests.md) |
| [`vktYCbCrStorageImageWriteTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp) | [`vktYCbCrStorageImageWriteTests.md`](../testfiles/ycbcr/vktYCbCrStorageImageWriteTests.md) |
| [`vktYCbCrImageOffsetTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp) | [`vktYCbCrImageOffsetTests.md`](../testfiles/ycbcr/vktYCbCrImageOffsetTests.md) |
| [`vktYCbCrMiscTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp) | [`vktYCbCrMiscTests.md`](../testfiles/ycbcr/vktYCbCrMiscTests.md) |

## Subgroup Structure and Major Themes

| Subgroup | Source-backed theme |
|---|---|
| [`format`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L734-L737) | Samples each generated YCbCr format subgroup through `VkSamplerYcbcrConversion`; generation covers shader stages, optimal/linear tiling, array layers, disjoint cases, mapped linear memory, and descriptor-set/buffer/heap modes where supported by [`populatePerFormatGroup()`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L640-L710). |
| [`filtering`](../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L787-L835) | Registers graphics and compute linear-sampler cases for eight 4:2:0 formats and two chroma-filter choices, then verifies sampled output through [`verifyFilteringResult()`](../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L206-L265). |
| [`plane_view`](../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L1065-L1078) | Registers `image_view` and `memory_alias` view types; per-case generation skips single-plane formats, requires disjoint planes for memory aliases, and adds compatible-format variants from the plane compatibility table in [`populateViewTypeGroup()`](../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L983-L1062). |
| [`query`](../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L593-L605) | Registers `size_lod` and `levels`; each shader-stage group includes `VK_FORMAT_R8G8B8A8_UNORM` as a reference plus YCbCr formats and disjoint variants from [`populateQueryInShaderGroup()`](../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L548-L577). |
| [`conversion`](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L2192-L2195) | Builds color-conversion, chroma-reconstruction, one-to-one, and sampler-array cases for source-defined format families in [`YCbCrConversionTestBuilder::buildTests()`](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1362-L2180). |
| [`copy`](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L1023-L1036) | Registers default copy, single-planar 422 copy, and dimension-stress copy groups; generation filters for YCbCr-involved and copy-compatible pairs in [`initYcbcrDefaultCopyTests()`](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L807-L867) and [`initYcbcrDimensionsCopyTests()`](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L923-L1018). |
| [`storage_image_write`](../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L939-L942) | Writes each plane from compute via storage-image descriptors, with joint and disjoint cases per aligned size from [`populateStorageImageWriteFormatGroup()`](../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L884-L934). |
| [`subresource_offset`](../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L167-L170) | Checks linear disjoint plane subresource offsets for formats in `formats::disjointPlanesFormats` registered by [`initYcbcrImageOffsetTests()`](../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L154-L162). |
| [`misc`](../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L366-L370) | Currently registers only `relaxed_precision`, a SPIR-V assembly test for relaxed precision on YCbCr sampler operations in [`RelaxedPrecisionTestCase::initPrograms()`](../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L299-L364). |

## Recurring Parameter Dimensions

| Dimension | Evidence-backed examples |
|---|---|
| Format ranges | Several files iterate `VK_YCBCR_FORMAT_FIRST` to `VK_YCBCR_FORMAT_LAST` and the 2-plane 444 EXT range, for example [`populateFormatGroup()`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L712-L729), [`populateQueryInShaderGroup()`](../../modules/vulkan/ycbcr/vktYCbCrImageQueryTests.cpp#L553-L576), and [`populateStorageImageWriteFormatGroup()`](../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L923-L932). |
| Chroma offsets and filters | Conversion tests vary chroma locations, texture filters, chroma filters, explicit reconstruction, disjoint state, tiling, and sampler bindings in [`YCbCrConversionTestBuilder::buildTests()`](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L1505-L1784) and [`buildArrayOfSamplersTests()`](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L2141-L2180). |
| Descriptor binding paths | `format` and `plane_view` add descriptor-set, descriptor-buffer, and descriptor-heap variants guarded by executor support in [`populatePerFormatGroup()`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L655-L672) and [`populateViewTypeGroup()`](../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L991-L1026). |
| Copy dimensions and formats | Copy stress uses five representative formats and sixteen wide/tall dimensions from [`initYcbcrDimensionsCopyTests()`](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L927-L951). |

## Recurring Support Requirements

- Shared YCbCr image-support checks require `VK_KHR_bind_memory2` and `VK_KHR_get_memory_requirements2` for disjoint images when those extensions are not core, and require midpoint or cosited chroma-sample format features for YCbCr formats in [`checkImageSupport()`](../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L176-L201).
- Sampler-conversion tests explicitly require `VK_KHR_sampler_ycbcr_conversion` and the `samplerYcbcrConversion` feature in files such as [`LinearFilteringTestCase::checkSupport()`](../../modules/vulkan/ycbcr/vktYCbCrFilteringTests.cpp#L704-L710), [`checkSupport()` for conversion](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L588-L595), and [`checkSupport()` for copy](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L185-L190).
- Descriptor-buffer and descriptor-heap variants are gated by `VK_EXT_descriptor_buffer` and `VK_EXT_descriptor_heap` in [`vktYCbCrFormatTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L332-L336) and [`vktYCbCrViewTests.cpp`](../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L496-L500).
- Storage-image-write disjoint cases require bind-memory extensions when needed, disjoint format support, and storage-image support on either the whole format or plane-compatible formats in [`checkSupport()`](../../modules/vulkan/ycbcr/vktYCbCrStorageImageWriteTests.cpp#L89-L215).

## Recurring Verification Methods

- Precision-bounded YCbCr sampling uses [`calculateBounds()`](../../modules/vulkan/ycbcr/vktYCbCrUtil.cpp#L1625) in conversion and filtering paths, including the conversion path's midpoint fallback for implicit-nearest cosited cases in [`textureConversionTest()`](../../modules/vulkan/ycbcr/vktYCbCrConversionTests.cpp#L803-L815).
- Format and plane-view tests execute shaders through `ShaderExecutor` and compare results to `tcu::Texture2DView::sample()` software references with a `0.02f` threshold in [`testFormat()`](../../modules/vulkan/ycbcr/vktYCbCrFormatTests.cpp#L541-L590) and [`testPlaneView()`](../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L806-L860).
- Copy tests build byte-level references from copied regions, mask don't-care packed-format bits, and fail after logging byte mismatches in [`imageCopyTest()`](../../modules/vulkan/ycbcr/vktYCbCrCopyTests.cpp#L663-L755).
- Subresource-offset tests bind each plane separately and inspect `vkGetImageSubresourceLayout` results in [`imageOffsetTest()`](../../modules/vulkan/ycbcr/vktYCbCrImageOffsetTests.cpp#L93-L139).

## Notes / Uncertainties

- The inspected source, not this page, is authoritative for exact generated case counts because several generators filter by format support, executor support, and extension availability at runtime.
- The `misc` group currently contains only `relaxed_precision` in [`createMiscTests()`](../../modules/vulkan/ycbcr/vktYCbCrMiscTests.cpp#L366-L370).
