# vktWsiIncrementalPresentTests

## Overview

Tests for the `VK_KHR_incremental_present` extension. This extension allows applications to specify which regions of the swapchain image have been updated since the last present, enabling the presentation engine to optimize by only processing the changed areas rather than the full image.

Each test renders a sequence of frames with incrementally updated rectangular regions and presents them using `VkPresentRegionsKHR` to describe the changed areas. A corresponding reference test presents the same frames without incremental present (using standard `VkPresentInfoKHR` with no regions), allowing behavioral comparison between incremental and full-present paths.

## Role of file

Implementation file. Contains the test instance logic, swapchain lifecycle management, rendering, and present submission with incremental present regions.

## Source code

[vktWsiIncrementalPresentTests.cpp](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp)

## Registration Hierarchy

```text
wsi.headless.incremental_present
└── scale_none
```

The `scale_up` and `scale_down` groups are conditionally registered only for WSI platform types where `PlatformProperties::swapchainExtent` equals `SWAPCHAIN_EXTENT_SCALED_TO_WINDOW_SIZE`, and are explicitly excluded for Wayland. They are not always present and therefore do not appear in the tree above.

## Test Families

### scale_none

Tests where the swapchain image extent matches the surface's current extent (no scaling applied). This group is always registered regardless of platform.

Each child under `scale_none` is a present mode group (e.g., `immediate`, `mailbox`, `fifo`, `fifo_relaxed`, `fifo_latest_ready`). Below each present mode group are transform groups, and below each transform group are composite alpha groups. At the leaf level, each alpha group contains two test cases:

- **reference** -- Presents frames using standard `VkPresentInfoKHR` without `VkPresentRegionsKHR` (incremental present disabled, `useIncrementalPresent = false`).
- **incremental_present** -- Presents frames using `VkPresentRegionsKHR` attached to `VkPresentInfoKHR::pNext` to specify the updated rectangular regions (incremental present enabled, `useIncrementalPresent = true`).

### scale_up (conditional)

Tests where the swapchain image extent is smaller than the surface extent (upscaling). Only registered when the platform's swapchain extent property is `SWAPCHAIN_EXTENT_SCALED_TO_WINDOW_SIZE` and the WSI type is not Wayland. Contains the same sub-hierarchy as `scale_none`.

### scale_down (conditional)

Tests where the swapchain image extent is larger than the surface extent (downscaling). Only registered under the same conditions as `scale_up`. Contains the same sub-hierarchy as `scale_none`.

## Parameter Dimensions

### Present Modes

Five present modes are iterated at [line 1089-1093](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1089-L1093):

| Name | VkPresentModeKHR |
|------|-----------------|
| `immediate` | `VK_PRESENT_MODE_IMMEDIATE_KHR` |
| `mailbox` | `VK_PRESENT_MODE_MAILBOX_KHR` |
| `fifo` | `VK_PRESENT_MODE_FIFO_KHR` |
| `fifo_relaxed` | `VK_PRESENT_MODE_FIFO_RELAXED_KHR` |
| `fifo_latest_ready` | `VK_PRESENT_MODE_FIFO_LATEST_READY_KHR` |

Tests skip with `NotSupportedError` if the present mode is not supported by the surface.

### Surface Transforms

Nine surface transform flags are iterated at [line 1098-1106](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1098-L1106):

| Name | Flag |
|------|------|
| `identity` | `VK_SURFACE_TRANSFORM_IDENTITY_BIT_KHR` |
| `rotate_90` | `VK_SURFACE_TRANSFORM_ROTATE_90_BIT_KHR` |
| `rotate_180` | `VK_SURFACE_TRANSFORM_ROTATE_180_BIT_KHR` |
| `rotate_270` | `VK_SURFACE_TRANSFORM_ROTATE_270_BIT_KHR` |
| `horizontal_mirror` | `VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_BIT_KHR` |
| `horizontal_mirror_rotate_90` | `VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_90_BIT_KHR` |
| `horizontal_mirror_rotate_180` | `VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_180_BIT_KHR` |
| `horizontal_mirror_rotate_270` | `VK_SURFACE_TRANSFORM_HORIZONTAL_MIRROR_ROTATE_270_BIT_KHR` |
| `inherit` | `VK_SURFACE_TRANSFORM_INHERIT_BIT_KHR` |

Tests skip with `NotSupportedError` if the transform is not in `supportedTransforms`.

### Composite Alpha

Four composite alpha flags are iterated at [line 1111-1114](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1111-L1114):

| Name | Flag |
|------|------|
| `opaque` | `VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR` |
| `pre_multiplied` | `VK_COMPOSITE_ALPHA_PRE_MULTIPLIED_BIT_KHR` |
| `post_multiplied` | `VK_COMPOSITE_ALPHA_POST_MULTIPLIED_BIT_KHR` |
| `inherit` | `VK_COMPOSITE_ALPHA_INHERIT_BIT_KHR` |

Tests skip with `NotSupportedError` if the alpha mode is not in `supportedCompositeAlpha`.

### Scaling

Three scaling modes are defined at [line 1082-1084](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1082-L1084):

| Name | Behavior |
|------|----------|
| `scale_none` | Swapchain image extent matches surface current extent |
| `scale_up` | Swapchain image extent is smaller (minimum 31 pixels, clamped to `minImageExtent`) |
| `scale_down` | Swapchain image extent is larger (next power-of-two above current extent, clamped to `maxImageExtent`) |

### Surface Formats

Rather than iterating all surface formats, the test selects a representative subset via `selectRepresentativeFormats` at [line 578-605](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L578-L605): it attempts to select one format with `SRGB_NONLINEAR_KHR` color space and one format with a non-SRGB color space. If no non-SRGB format exists, only the SRGB format is selected. If neither criterion matches, `formats[0]` is used as a fallback. For each selected format, two swapchain configurations are generated: one at the test extent and one at an "unused" extent.

## Support / Feature Requirements

- **Instance extensions**: `VK_KHR_surface`, the platform-specific surface extension (e.g., `VK_KHR_headless_surface`), and conditionally `VK_KHR_display`, `VK_EXT_direct_mode_display`, `VK_EXT_swapchain_colorspace`.
- **Device extensions**: `VK_KHR_swapchain` is always required. `VK_KHR_incremental_present` is required for the `incremental_present` test variant (enabled via `requiresIncrementalPresent` parameter in `createDeviceWithWsi` at [line 107](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L107)). `VK_EXT_swapchain_colorspace` and `VK_EXT_present_mode_fifo_latest_ready` are enabled if supported.
- **Feature**: `presentModeFifoLatestReady` from `VkPhysicalDevicePresentModeFifoLatestReadyFeaturesKHR` is enabled when the `fifo_latest_ready` extension is available at [line 116-117](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L116-L117).
- Tests throw `NotSupportedError` if required extensions, present modes, transforms, or composite alpha modes are not available.

## Verification Methods

The test does not perform pixel-level validation of presented content. Instead, verification is behavioral:

1. **Successful presentation**: The test renders 300 frames (60 * 5 at [line 762](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L762)) per swapchain configuration and verifies that `vkQueuePresentKHR` returns a successful `VkResult` for each frame, both with and without `VkPresentRegionsKHR`.
2. **Incremental present regions**: For the `incremental_present` variant, `VkPresentRegionsKHR` is populated with the rectangles of updated regions computed by `getUpdatedRects` at [line 245-258](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L245-L258). The test verifies the presentation engine accepts these regions without error.
3. **Swapchain out-of-date handling**: If `VK_ERROR_OUT_OF_DATE_KHR` or `VK_SUBOPTIMAL_KHR` is received, the test recreates the swapchain and retries up to 20 times (at [line 765](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L765)). Exceeding this limit results in a failure recorded via `tcu::ResultCollector`.
4. **Multiple swapchain configurations**: The test iterates through all generated swapchain configurations (representative formats x 2, including an "unused" swapchain per format), verifying incremental present works across different format and extent combinations.

## Notes / Uncertainties

- The `scale_up` and `scale_down` groups are conditionally registered based on `vk::wsi::getPlatformProperties(wsiType).swapchainExtent == SWAPCHAIN_EXTENT_SCALED_TO_WINDOW_SIZE`. For the headless platform, whether these groups appear depends on the headless platform's property definition, which is external to this file.
- The `fifo_latest_ready` present mode requires `VK_EXT_present_mode_fifo_latest_ready` device extension and the `presentModeFifoLatestReady` feature. Tests using this mode will skip if the extension or feature is not available.
- The "unused" swapchain configuration (at [line 696-715](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L696-L715)) is created alongside the primary swapchain for each format, exercising the `oldSwapchain` parameter path implicitly through swapchain recreation, though the unused swapchain itself is not directly presented.
- The test does not compare visual output between the `reference` and `incremental_present` variants; it only verifies that both paths complete without Vulkan errors.
- Wayland explicitly excludes `scale_up` and `scale_down` at [line 1118-1119](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1118-L1119).
