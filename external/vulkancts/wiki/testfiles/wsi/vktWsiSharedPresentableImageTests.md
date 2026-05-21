# vktWsiSharedPresentableImageTests

## Overview

Tests for the `VK_KHR_shared_presentable_image` extension. These tests verify that a swapchain created with a shared presentable image (single-image swapchain) operates correctly under the two shared present modes: `VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR` and `VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR`. The test renders multiple frames to a single acquired image and validates present behavior, swapchain status queries, and resource lifecycle management.

## Role of file

Implementation file. Contains the test instance logic, swapchain creation, rendering loop, and test group registration for shared presentable image WSI tests.

## Source code

[vktWsiSharedPresentableImageTests.cpp](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp)

## Registration Hierarchy

```text
wsi.headless.shared_presentable_image
└── scale_none
```

Note: `scale_up` and `scale_down` are conditionally registered as additional direct children only when the WSI platform supports scaled swapchain extents (i.e., when `PlatformProperties::SWAPCHAIN_EXTENT_SCALED_TO_WINDOW_SIZE` matches the platform's swapchain extent property). They are not registered on platforms with fixed swapchain extents.

## Test Families

### scale_none

Tests shared presentable image behavior with the swapchain image extent matching the surface's current extent (no scaling). This group is always registered regardless of platform.

Under `scale_none`, the hierarchy continues as:

- **Transform groups** (one per `VkSurfaceTransformFlagBitsKHR` value):
  - `identity`, `rotate_90`, `rotate_180`, `rotate_270`, `horizontal_mirror`, `horizontal_mirror_rotate_90`, `horizontal_mirror_rotate_180`, `horizontal_mirror_rotate_270`, `inherit`
  - Each transform group contains **alpha groups** (one per `VkCompositeAlphaFlagBitsKHR` value):
    - `opaque`, `pre_multiplied`, `post_multiplied`, `inherit`
    - Each alpha group contains **present mode leaf tests**:
      - `demand` - tests `VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR`
      - `continuous` - tests `VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR`

### scale_up (conditional)

Tests shared presentable image behavior with the swapchain image extent set smaller than the surface extent (upscaling). Only registered when the WSI platform supports scaled swapchain extents. Internal structure mirrors `scale_none`.

### scale_down (conditional)

Tests shared presentable image behavior with the swapchain image extent set larger than the surface extent (downscaling). Only registered when the WSI platform supports scaled swapchain extents. Internal structure mirrors `scale_none`.

## Parameter Dimensions

| Dimension | Values | Notes |
|-----------|--------|-------|
| Scaling | `scale_none`, `scale_up`, `scale_down` | `scale_up` and `scale_down` are conditional on platform support |
| Present Mode | `VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR`, `VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR` | The two shared present modes defined by the extension |
| Surface Transform | `IDENTITY`, `ROTATE_90`, `ROTATE_180`, `ROTATE_270`, `HORIZONTAL_MIRROR`, `HORIZONTAL_MIRROR_ROTATE_90`, `HORIZONTAL_MIRROR_ROTATE_180`, `HORIZONTAL_MIRROR_ROTATE_270`, `INHERIT` | 9 transform flags; each throws `NotSupportedError` if not supported by the surface |
| Composite Alpha | `OPAQUE`, `PRE_MULTIPLIED`, `POST_MULTIPLIED`, `INHERIT` | 4 alpha flags; each throws `NotSupportedError` if not supported by the surface |
| Surface Format | All formats returned by `getPhysicalDeviceSurfaceFormats` | Iterated automatically per swapchain config; skipped if `getPhysicalDeviceImageFormatProperties` returns `VK_ERROR_FORMAT_NOT_SUPPORTED` |

## Support/Feature Requirements

- **VK_KHR_shared_presentable_image** extension is required (enabled on the device alongside `VK_KHR_swapchain`)
- **VK_KHR_surface** and **VK_KHR_get_surface_capabilities2** instance extensions are required
- The platform-specific WSI surface extension is required (e.g., `VK_KHR_headless_surface` for headless)
- `VK_KHR_get_physical_device_properties2` is required if not a core extension at the used API version
- The surface must support the requested present mode, transform, and composite alpha values (otherwise `NotSupportedError` is thrown)
- `VkSharedPresentSurfaceCapabilitiesKHR::sharedPresentSupportedUsageFlags` must include `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT` (checked at [vktWsiSharedPresentableImageTests.cpp#L596](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L596))

## Verification Methods

- **Swapchain creation**: Creates a single-image swapchain (`minImageCount = 1`) with the specified shared present mode, transform, alpha, and format ([vktWsiSharedPresentableImageTests.cpp#L539-L556](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L539-L556))
- **Image acquisition**: Acquires the single swapchain image upfront via `acquireNextImageKHR` and verifies the image index is 0 ([vktWsiSharedPresentableImageTests.cpp#L699-L701](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L699-L701))
- **Layout transition**: Transitions the image from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR` and keeps it in that layout for the entire test duration ([vktWsiSharedPresentableImageTests.cpp#L710-L724](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L710-L724))
- **Rendering loop**: Renders 300 frames (60 * 5) per swapchain configuration using a graphics pipeline with push-constant-driven fragment shader output ([vktWsiSharedPresentableImageTests.cpp#L643](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L643))
- **Present mode behavior**:
  - For `SHARED_DEMAND_REFRESH`: calls `queuePresentKHR` every frame to ensure the presentation engine picks up updates ([vktWsiSharedPresentableImageTests.cpp#L775-L827](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L775-L827))
  - For `SHARED_CONTINUOUS_REFRESH`: calls `queuePresentKHR` only on the first frame to kick off presentation ([vktWsiSharedPresentableImageTests.cpp#L775-L778](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L775-L778))
- **Swapchain status query**: Calls `getSwapchainStatusKHR` every frame to detect `VK_ERROR_OUT_OF_DATE_KHR` conditions ([vktWsiSharedPresentableImageTests.cpp#L832-L833](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L832-L833))
- **Out-of-date recovery**: Handles `VK_ERROR_OUT_OF_DATE_KHR` by recreating swapchain resources, up to a maximum of 20 times before failing ([vktWsiSharedPresentableImageTests.cpp#L856-L896](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L856-L896))
- **Vulkan result checking**: All Vulkan API calls are wrapped with `VK_CHECK` / `VK_CHECK_WSI` macros

## Notes/Uncertainties

- The render pass uses `VK_ATTACHMENT_LOAD_OP_LOAD` with `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR` for both initial and final layouts, which is intentional for shared presentable images to avoid discarding content that the presentation engine may be accessing concurrently ([vktWsiSharedPresentableImageTests.cpp#L319-L331](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L319-L331))
- The test does not perform pixel-level verification of rendered output; it validates that the swapchain operations and presentation flow complete without errors
- The frame count of 300 (60 * 5) appears to be a fixed duration test rather than a frame-count test, though the exact rationale (e.g., 5 seconds at 60 FPS) is not documented in the source
- The `SCALING_UP` extent calculation uses `de::max(31u, properties.minImageExtent.width/height)` which may not always produce a size smaller than the surface extent depending on surface capabilities
- Conditional registration of `scale_up` and `scale_down` depends on `wsiTypeSupportsScaling()`, which checks whether the platform's `SWAPCHAIN_EXTENT` property is `SWAPCHAIN_EXTENT_SCALED_TO_WINDOW_SIZE`
