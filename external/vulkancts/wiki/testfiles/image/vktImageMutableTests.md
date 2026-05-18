# [vktImageMutableTests.cpp](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1)

## Overview

[`vktImageMutableTests.cpp`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1) is an implementation-heavy Level-3 file for the `image.mutable` and `image.swapchain_mutable` subtrees. It covers Vulkan mutable image format scenarios, testing scenarios where an image is created with one format but views are created with compatible but different formats. The file tests various upload/download method combinations, multisample resolve attachments with mutable formats, and swapchain mutable format functionality.

## Role of File

- **Role:** implementation-heavy test file.
- **Primary source:** [`vktImageMutableTests.cpp`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1).
- **Registration context inspected:**
  - [`vktImageTests.cpp`](../../../modules/vulkan/image/vktImageTests.cpp) for placement under the top-level `image` category.
  - [`createImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1856-L1985) for the Level-3 root `image.mutable`.
  - [`createSwapchainImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2372-L2438) for the Level-3 root `image.swapchain_mutable`.

## Source Code

- Implementation: [vktImageMutableTests.cpp](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1)
- Header: [vktImageMutableTests.hpp](../../../modules/vulkan/image/vktImageMutableTests.hpp#L1)
- Parent registration: [vktImageTests.cpp](../../../modules/vulkan/image/vktImageTests.cpp)

## Registration Hierarchy

```text
image.mutable
└── (test groups by image type: 2d, 2d_array)
    └── (test cases by format combination and upload/download methods)

image.swapchain_mutable
└── (test groups by WSI type: egl, glx, platform, wayland, xcb, xlib)
    └── (test groups by image type: 2d, 2d_array)
        └── (test cases by format combination and upload/download methods)
```

The confirmed Level-3 roots are `image.mutable` (created by [`createImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1856-L1985)) and `image.swapchain_mutable` (created by [`createSwapchainImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2372-L2438)). Both register under `image` in [`vktImageTests.cpp`](../../../modules/vulkan/image/vktImageTests.cpp).

## Test Families

### mutable �?Mutable image format testing

Covers the `mutable` direct child registered by [`createImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1856-L1985). This group tests scenarios where image views are created with formats different from but compatible with the underlying image format.

The test structure creates subgroups by image view type (`2d`, `2d_array`), then generates test cases for format pairs where the formats differ but are compatible (same pixel size) according to [`formatsAreCompatible()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L290-L293).

### swapchain_mutable �?Swapchain mutable format testing

Covers the `swapchain_mutable` direct child registered by [`createSwapchainImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2372-L2438). This group tests mutable format functionality specifically for swapchain images, using the WSI surface formats defined in [`s_swapchainFormats[]`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L262-L265).

The test structure organizes by WSI type, then by image view type, with generated test cases for compatible format pairs.

## Parameter Dimensions

| Dimension | Observed values / construction | Evidence |
|---|---|---|
| Level-3 direct children | `mutable`, `swapchain_mutable` | [`createImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1856-L1985), [`createSwapchainImageMutableTests()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2372-L2438) |
| Image view types | `2d`, `2d_array` | [`s_textures[]`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L165-L168) |
| Image dimensions | 32x32x1 | [`s_textures[]`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L165-L168) |
| Array layers | 1 (2d), 4 (2d_array) | [`s_textures[]`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L165-L168) |
| Format array (mutable) | 20 formats including float, uint, sint, and unorm/snorm/srgb variants | [`s_formats[]`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L248-L260) |
| Format array (swapchain) | 6 formats: R8G8B8A8_UNORM/SNORM/SRGB, B8G8R8A8_UNORM/SNORM/SRGB | [`s_swapchainFormats[]`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L262-L265) |
| Upload methods | `clear`, `copy`, `store`, `draw` | [`Upload enum`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L78-L85) |
| Download methods | `copy`, `load`, `texture` | [`Download enum`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L87-L93) |
| Resolve attachment types | `RA_TEST_NONE`, `RA_TEST_ALL_MUTABLE`, `RA_TEST_RA_MUTABLE`, `RA_TEST_CA_MUTABLE` | [`ResolveAttachmentTestType`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L107-L113) |
| Format list test | `false`, `true` (VK_KHR_image_format_list) | [`CaseDef.isFormatListTest`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L124) |
| Load op clear test | `false`, `true` | [`CaseDef.isLoadOpClearTest`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L127) |
| WSI types | All types in `vk::wsi::Type` enum | [`vk::wsi::TYPE_LAST`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2376) |
| Color table entries | 4 reference colors for float and integer formats | [`COLOR_TABLE_FLOAT[]`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L135-L140), [`COLOR_TABLE_INT[]`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L146-L151) |

## Support / Feature Requirements

Observed support gates and extension-dependent coverage include:

| Feature / Extension | When it applies | Evidence |
|---|---|---|
| `VK_KHR_image_format_list` | Tests with `isFormatListTest = true` | [`CaseDef.isFormatListTest`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L124), [`checkSupport()``](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1777-L1779) |
| `VK_KHR_maintenance2` | Required for `VK_IMAGE_CREATE_EXTENDED_USAGE_BIT` usage | [`checkSupport()``](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1827-L1838) |
| `VK_KHR_swapchain` | Swapchain mutable tests | [`createDeviceWithWsi()``](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2056) |
| `VK_KHR_swapchain_mutable_format` | Swapchain mutable tests | [`createDeviceWithWsi()``](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2056) |
| `VK_EXT_swapchain_colorspace` | Swapchain color space extension (optional) | [`createInstanceWithWsi()``](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2033-L2034) |
| `VK_EXT_direct_mode_display` | DRM-specific WSI type | [`createInstanceWithWsi()``](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2011-L2012) |
| `VK_EXT_physical_device_drm` | DRM-specific WSI type | [`createInstanceWithWsi()``](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2015-L2016) |
| Format feature flags | Required format features depend on upload/download method | [`checkSupport()``](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1787-L1825) |
| Multisampling support | Validated via `getMaxAvailableSampleCount()` | [`checkSupport()``](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1851-L1853) |

## Verification Methods

- **Image content comparison:** Tests use [`tcu::floatThresholdCompare()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1766-L1767) for floating-point formats and [`tcu::intThresholdCompare()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1763-L1764) for integer formats.
- **Expected image generation:** The [`generateExpectedImage()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L819-L846) function generates expected pixel values based on the color table and upload method, including sRGB conversion when required.
- **Color table cycling:** Each layer uses a different color from the color table, cycling through 4 entries.
- **sRGB conversion handling:** Tests properly handle sRGB linearization/gamma conversion based on image format and upload method per [`isSRGBConversionRequired()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L267-L288).

## Test Principles Observed

- **Format compatibility is determined by pixel size.** The [`formatsAreCompatible()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L290-L293) function checks if two formats have the same pixel size, enabling format-compatible but differently-typed views.
- **Upload/download method matrix covers all combinations.** Four upload methods (clear, copy, store, draw) combined with three download methods (copy, load, texture) provide comprehensive coverage of image data pathways.
- **Resolve attachment tests validate multisample operations.** Tests cover scenarios where multisampled color attachments and single-sample resolve attachments have mutable/non-mutable combinations.
- **VK_KHR_image_format_list extends mutable format capability.** When enabled, images can specify multiple compatible formats in the image format list, extending the scenarios where mutable views are valid.
- **Swapchain image synchronization:** Swapchain mutable tests acquire an image from the swapchain before use and pass
  the acquire semaphore into the command-buffer submission so rendering/copy work waits for image availability
  ([acquire](../../../modules/vulkan/image/vktImageMutableTests.cpp#L2332-L2335),
  [submit wait](../../../modules/vulkan/image/vktImageMutableTests.cpp#L1076-L1078)).

## Notes / Uncertainties

- The file registers two separate Level-3 roots (`image.mutable` and `image.swapchain_mutable`) from a single source file, which is handled by separate factory functions.
- The `resolveAttachmentTestType` parameter generates multiple test variants per format pair, including `_resolve`, `_mutable_resolve_att`, and `_mutable_color_att` suffixes.
- `VK_IMAGE_CREATE_MUTABLE_FORMAT_BIT` is always set on images under test per [`makeImage()`](../../../modules/vulkan/image/vktImageMutableTests.cpp#L540-L573).
- Sparse residency testing is not included in this file; it focuses on standard mutable format scenarios.
