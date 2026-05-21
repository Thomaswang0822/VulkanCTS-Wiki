# vktWsiTests

## Overview

This is the root registration/dispatcher file for the WSI (Window System Integration) test category. It constructs the entire WSI test tree by iterating over all `vk::wsi::Type` enum values to create per-platform groups (each containing an identical set of sub-groups), then appends three cross-platform display-related groups. The file contains no test logic itself; its sole purpose is registration and delegation.

## Role

Registration file — contains the `createWsiTests` function that builds the WSI test tree and delegates to per-category registration functions.

## Source

[vktWsiTests.cpp](../../../modules/vulkan/wsi/vktWsiTests.cpp#L76-L91)

## Registration Hierarchy

```text
wsi
├── xlib
├── xcb
├── wayland
├── android
├── win32
├── metal
├── headless
├── direct_drm
├── direct
├── display
├── display_control
└── acquire_drm_display
```

## Test Families

### Per-Platform Groups

The first nine children (xlib through direct) are per-WSI-platform-type groups. Each is created by iterating over the `vk::wsi::Type` enum ([vkDefs.hpp#L205-L218](../../../framework/vulkan/vkDefs.hpp#L205-L218)) and registered via `getName(wsiType)` ([vkWsiUtil.cpp#L65-L71](../../../framework/vulkan/vkWsiUtil.cpp#L65-L71)). Every per-platform group contains the same sub-group structure, created by `createTypeSpecificTests` ([vktWsiTests.cpp#L50-L74](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L74)):

- **surface** — VkSurface creation and query tests
- **swapchain** — VkSwapchain creation and operation tests
- **incremental_present** — VK_KHR_incremental_present tests
- **display_timing** — VK_EXT_display_timing tests
- **shared_presentable_image** — VK_KHR_shared_presentable_image tests
- **colorspace** — Color space enumeration and query tests
- **colorspace_compare** — Color space comparison tests
- **full_screen_exclusive** — VK_EXT_full_screen_exclusive tests
- **present_id_wait** — VK_KHR_present_id / VK_KHR_present_wait tests
- **maintenance1** — VK_KHR_surface_maintenance1 / VK_KHR_swapchain_maintenance1 tests
- **present_timing** — VK_EXT_present_timing tests

Individual per-platform groups:

- **xlib** — X11 Xlib platform (`TYPE_XLIB`, requires `VK_KHR_xlib_surface`)
- **xcb** — X11 XCB platform (`TYPE_XCB`, requires `VK_KHR_xcb_surface`)
- **wayland** — Wayland platform (`TYPE_WAYLAND`, requires `VK_KHR_wayland_surface`)
- **android** — Android platform (`TYPE_ANDROID`, requires `VK_KHR_android_surface`)
- **win32** — Windows Win32 platform (`TYPE_WIN32`, requires `VK_KHR_win32_surface`)
- **metal** — Apple Metal platform (`TYPE_METAL`, requires `VK_EXT_metal_surface`)
- **headless** — Headless (off-screen) platform (`TYPE_HEADLESS`, requires `VK_EXT_headless_surface`). Used as the representative platform in documentation.
- **direct_drm** — Direct DRM platform (`TYPE_DIRECT_DRM`, requires `VK_EXT_acquire_drm_display`)
- **direct** — Direct display platform (`TYPE_DIRECT`, requires `VK_KHR_display`)

### Cross-Platform Groups

The last three children do not take a `wsiType` parameter and are not tied to a specific windowing system:

- **display** — Cross-platform display coverage tests, registered via `createDisplayCoverageTests`
- **display_control** — Cross-platform display control tests (VK_EXT_display_control), registered via `createDisplayControlTests`
- **acquire_drm_display** — Cross-platform DRM display acquisition tests, registered via `createAcquireDrmDisplayTests`

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| wsiType | xlib, xcb, wayland, android, win32, metal, headless, direct_drm, direct | The `vk::wsi::Type` enum iterated from `TYPE_XLIB` (0) to `TYPE_DIRECT` (8). Passed to each per-platform sub-group registration function. |

The cross-platform groups (display, display_control, acquire_drm_display) do not accept a `wsiType` parameter.

## Support / Feature Requirements

- Each per-WSI-type group requires the corresponding platform to be available at test runtime; unsupported platforms are skipped by the test executor.
- Each per-WSI-type group requires the corresponding Vulkan surface extension (e.g., `VK_KHR_xlib_surface`, `VK_KHR_win32_surface`, `VK_EXT_headless_surface`).
- The display, display_control, and acquire_drm_display groups are cross-platform and do not depend on a specific WSI surface type, but may require VK_KHR_display or related extensions.

## Verification Methods

- This file performs registration only; all verification is delegated to the individual sub-group implementation files (e.g., vktWsiSurfaceTests, vktWsiSwapchainTests, etc.).

## Notes / Uncertainties

- The WSI type loop iterates from `TYPE_XLIB = 0` through `TYPE_LAST` (exclusive), covering 9 platform types. The `getName()` function ([vkWsiUtil.cpp#L65-L71](../../../framework/vulkan/vkWsiUtil.cpp#L65-L71)) maps each enum value to its string name used in the test path.
- The three cross-platform groups (display, display_control, acquire_drm_display) are added after the per-type loop and are not parameterized by WSI type.
- The `getExtensionName()` function ([vkWsiUtil.cpp#L73-L80](../../../framework/vulkan/vkWsiUtil.cpp#L73-L80)) maps each type to its required Vulkan extension name.
