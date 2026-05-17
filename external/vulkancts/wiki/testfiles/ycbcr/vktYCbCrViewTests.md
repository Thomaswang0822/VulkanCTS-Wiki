# vktYCbCrViewTests.cpp

## Overview

Tests plane-level image view access of multi-planar YCbCr images. Verifies that sampling individual planes through image views with compatible formats produces the same results as sampling the whole image through a YCbCr conversion-enabled view. Supports both direct image view access and memory aliasing approaches.

**Role:** Implementation (registers group `ycbcr.plane_view`)

**Source:** [vktYCbCrViewTests.cpp](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp)

## Registration Hierarchy

```text
ycbcr.plane_view
├── image_view
└── memory_alias
```

## Test Families

### plane_view

Verifies that individual planes of a multi-planar YCbCr image can be accessed via image views with the plane's compatible format (or a format-compatible alternative). The test samples both the whole image (with YCbCr conversion) and the individual plane view, then compares the results against software reference values.

**View Types:**

| View Type | Description |
|-----------|-------------|
| `image_view` | Creates a `VkImageView` with `VK_IMAGE_ASPECT_PLANE_N_BIT` on the original multi-planar image |
| `memory_alias` | Creates a separate image bound to the same memory as the plane, with `VK_IMAGE_CREATE_ALIAS_BIT` (requires disjoint) |

**Parameter Dimensions:**

| Dimension | Values | Notes |
|-----------|--------|-------|
| Format | All YCbCr multi-planar formats (`VK_YCBCR_FORMAT_FIRST` through `VK_YCBCR_FORMAT_LAST`, plus 444 EXT formats) | Single-plane formats are skipped |
| Plane Index | 0 through `numPlanes-1` | Each plane is tested independently |
| Compatible Format | Plane's native compatible format, plus any format with matching pixel size from the compatibility table | E.g., `VK_FORMAT_R4G4_UNORM_PACK8` is compatible with `VK_FORMAT_R8_UNORM` |
| Disjoint | false, true | `VK_IMAGE_CREATE_DISJOINT_BIT` (memory_alias requires disjoint) |
| Shader Type | fragment, compute | Only shader stages with executor support |

**Support Requirements:**

- `VK_FORMAT_FEATURE_SAMPLED_IMAGE_BIT | VK_FORMAT_FEATURE_TRANSFER_DST_BIT | VK_FORMAT_FEATURE_MIDPOINT_CHROMA_SAMPLES_BIT` for the YCbCr format
- `VK_FORMAT_FEATURE_SAMPLED_IMAGE_BIT | VK_FORMAT_FEATURE_TRANSFER_DST_BIT` for the plane compatible format
- `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` is always set
- `VK_IMAGE_CREATE_ALIAS_BIT` for memory alias view type
- `VK_IMAGE_CREATE_DISJOINT_BIT` for disjoint tests (and required for memory alias)

**Verification Method:**

Shader execution via `ShaderExecutor`. Two outputs are produced: (1) the whole image sampled with YCbCr conversion, and (2) the plane view sampled without conversion. Both are compared against software reference values using `tcu::Texture2DView::sample()` with a threshold of 0.02f. For compatible format comparisons, a `chooseComparisonFormat()` function selects the appropriate format to handle padded formats (e.g., `R10X6` vs `R12X4`) where padding bits may differ.

**Key Functions:**

- [testPlaneView()](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L487) - Main test implementation
- [populateViewTypeGroup()](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L825) - Per-view-type test case generation
- [populateViewGroup()](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L891) - Top-level view group population
- [createViewTests()](../../../modules/vulkan/ycbcr/vktYCbCrViewTests.cpp#L901) - Factory function returning the `plane_view` group
