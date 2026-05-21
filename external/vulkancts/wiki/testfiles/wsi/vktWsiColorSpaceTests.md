# vktWsiColorSpaceTests

Tests for the `VK_EXT_swapchain_colorspace` and `VK_EXT_hdr_metadata` extensions, verifying that swapchains can be created and rendered with various color spaces and that color space selection does not affect pixel values read back from swapchain images. This file creates two separate test groups: `colorspace` and `colorspace_compare`.

**Role:** Implementation file

**Source:** [vktWsiColorSpaceTests.cpp](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp)

> **Per-Platform Note:** "headless" is used as the representative platform in the Level-3 root path below. The same structure is replicated for all WSI platform types (e.g., `wsi.xlib.colorspace`, `wsi.wayland.colorspace`, etc.).

## Registration Hierarchy

```text
wsi.headless.colorspace
├── extensions
├── basic
└── hdr
```

This file also registers a second top-level group at `wsi.headless.colorspace_compare` as a sibling of `colorspace`. That group contains six direct children, one per format: `b8g8r8a8_unorm`, `r8g8b8a8_unorm`, `r8g8b8a8_srgb`, `r5g6b5_unorm_pack16`, `a2b10g10r10_unorm_pack32`, and `r16g16b16a16_sfloat`.

## Test Families

### colorspace group

| Family | Description |
|--------|-------------|
| `extensions` | Extension support check. Verifies that `VK_EXT_swapchain_colorspace` is properly advertised and that at least one non-`SRGB_NONLINEAR_KHR` surface format is available. No rendering is performed. Implemented by [basicExtensionTest](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L385-L416). |
| `basic` | Rendering stress test. Iterates over all supported surface format + color space combinations reported by `getPhysicalDeviceSurfaceFormatsKHR`, creating a swapchain for each and rendering 60 frames via `WsiTriangleRenderer`. No pixel comparison is performed. Implemented by [surfaceFormatRenderTests](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L696-L717). |
| `hdr` | Rendering stress test with HDR metadata. Same as `basic` but additionally calls `setHdrMetadataEXT` with a `VkHdrMetadataEXT` struct on the swapchain. Requires `VK_EXT_hdr_metadata`. No pixel comparison is performed. Implemented by [surfaceFormatRenderWithHdrTests](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L719-L740). |

### colorspace_compare group

| Family | Description |
|--------|-------------|
| `b8g8r8a8_unorm` | Pixel comparison test for `VK_FORMAT_B8G8R8A8_UNORM`. Creates swapchains with each supported color space for this format, renders the same content, reads back the pixel at (128, 128), and compares across color spaces. |
| `r8g8b8a8_unorm` | Pixel comparison test for `VK_FORMAT_R8G8B8A8_UNORM`. Same verification method as above. |
| `r8g8b8a8_srgb` | Pixel comparison test for `VK_FORMAT_R8G8B8A8_SRGB`. Same verification method as above. |
| `r5g6b5_unorm_pack16` | Pixel comparison test for `VK_FORMAT_R5G6B5_UNORM_PACK16`. Same verification method as above. |
| `a2b10g10r10_unorm_pack32` | Pixel comparison test for `VK_FORMAT_A2B10G10R10_UNORM_PACK32`. Same verification method as above. |
| `r16g16b16a16_sfloat` | Pixel comparison test for `VK_FORMAT_R16G16B16A16_SFLOAT`. Same verification method as above. |

All six per-format tests are created by [createColorspaceCompareTests](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L765-L779) and share the same implementation function [colorspaceCompareTest](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L425-L563).

## Parameter Dimensions

| Dimension | Values | Source |
|-----------|--------|--------|
| Surface format + color space (colorspace group) | All combinations supported by the surface, iterated via `getPhysicalDeviceSurfaceFormatsKHR` | [L398-L399](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L398-L399) |
| Format (colorspace_compare group) | `VK_FORMAT_B8G8R8A8_UNORM`, `VK_FORMAT_R8G8B8A8_UNORM`, `VK_FORMAT_R8G8B8A8_SRGB`, `VK_FORMAT_R5G6B5_UNORM_PACK16`, `VK_FORMAT_A2B10G10R10_UNORM_PACK32`, `VK_FORMAT_R16G16B16A16_SFLOAT` | [L767-L769](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L767-L769) |
| Color space (colorspace_compare group) | All color spaces supported for the given format, as reported by `getPhysicalDeviceSurfaceFormatsKHR` | [L438-L448](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L438-L448) |
| HDR metadata (hdr test only) | Present or absent | [L661-L676](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L661-L676) |

## Support / Feature Requirements

- **VK_EXT_swapchain_colorspace** -- required for all tests in both groups. The extension is conditionally added to the instance extension list at [L120-L121](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L120-L121) (if supported), and the actual requirement check occurs at test execution time ([L394-L396](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L394-L396), [L427-L428](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L427-L428)), where `NotSupportedError` is thrown if the extension is not present.
- **VK_EXT_hdr_metadata** -- required for the `hdr` test only. Checked at device creation time ([L151-L152](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L151-L152)) and again at test execution time ([L581-L582](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L581-L582)).
- **VK_KHR_swapchain** -- required for all rendering tests ([L147-L149](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L147-L149)).
- **VK_KHR_surface** and platform-specific surface extension -- required for instance creation ([L100-L104](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L100-L104)).
- For `colorspace_compare`: at least 2 color spaces must be supported for the given format, otherwise the test is skipped ([L451-L452](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L451-L452)).
- For `extensions`: at least one surface format with a non-`SRGB_NONLINEAR_KHR` color space must be reported ([L401-L414](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L401-L414)).

## Verification Methods

- **Extension check (`extensions`):** Verifies that `VK_EXT_swapchain_colorspace` is supported and that the implementation reports at least one surface format with a color space other than `VK_COLOR_SPACE_SRGB_NONLINEAR_KHR`. No rendering or pixel comparison.
- **Rendering stress test (`basic`, `hdr`):** Renders 60 frames per surface format + color space combination using `WsiTriangleRenderer`. Passes if no Vulkan errors occur during swapchain creation, image acquisition, rendering, and presentation. No pixel comparison.
- **Pixel comparison (`colorspace_compare`):** For each supported color space of a given format, creates a swapchain, renders a triangle, and reads back the pixel at position (128, 128) via `getPixel`. The first color space serves as the reference; subsequent color spaces are compared against it using exact `tcu::Vec4` equality. Passes if all pixel values are identical across color spaces, confirming that color space selection does not alter the raw pixel data stored in the swapchain image.

## Notes / Uncertainties

- The `colorspace_compare` test assumes that the raw pixel values in swapchain images are independent of the color space flag. This is a reasonable assumption for the CTS validation model but may not reflect how a compositor interprets the color space at presentation time.
- The `basic` and `hdr` tests do not perform any pixel comparison; they only verify that swapchain creation and rendering complete without errors across all supported format + color space combinations.
- The `hdr` test sets HDR metadata via `setHdrMetadataEXT` but does not verify that the compositor or presentation engine actually uses it.
- The format list in `colorspace_compare` is hardcoded at [L767-L769](../../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp#L767-L769) and may not cover all formats that support multiple color spaces on a given implementation.
- The `extensions` test checks for non-`SRGB_NONLINEAR_KHR` formats but does not verify that any specific extended color space is usable for swapchain creation.
