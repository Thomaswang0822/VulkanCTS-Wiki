# WSI (Window System Integration)

## Overview

The WSI category tests Vulkan's Window System Integration functionality, covering surface creation, swapchain management, presentation, display control, and related extensions. WSI is the subsystem that connects Vulkan rendering to the operating system's windowing and display infrastructure.

The category has a unique two-tier structure: most test groups are replicated per WSI platform type (xlib, xcb, wayland, android, win32, metal, headless, direct_drm, direct), while three groups (display, display_control, acquire_drm_display) are cross-platform.

## Registration Entry Point

[vktWsiTests.cpp](../../modules/vulkan/wsi/vktWsiTests.cpp#L76-L91) — `createWsiTests()` registers the root "wsi" group.

## Subgroup Structure

### Per-Platform Groups

The root registration iterates over all 9 WSI platform types ([vkDefs.hpp](../../framework/vulkan/vkDefs.hpp#L205-L218)) and creates identical subgroup structures under each:

| Subgroup | Extension | Description | Level-3 Doc |
|----------|-----------|-------------|-------------|
| surface | VK_KHR_surface | Surface creation, queries, capabilities, formats, present modes | [vktWsiSurfaceTests](../testfiles/wsi/vktWsiSurfaceTests.md) |
| swapchain | VK_KHR_swapchain | Swapchain creation, destruction, rendering, image acquisition | [vktWsiSwapchainTests](../testfiles/wsi/vktWsiSwapchainTests.md) |
| incremental_present | VK_KHR_incremental_present | Incremental present with scaling/transform/present-mode combinations | [vktWsiIncrementalPresentTests](../testfiles/wsi/vktWsiIncrementalPresentTests.md) |
| display_timing | VK_GOOGLE_display_timing | Display timing with present-mode variants | [vktWsiDisplayTimingTests](../testfiles/wsi/vktWsiDisplayTimingTests.md) |
| shared_presentable_image | VK_KHR_shared_presentable_image | Shared presentable image with demand/continuous modes | [vktWsiSharedPresentableImageTests](../testfiles/wsi/vktWsiSharedPresentableImageTests.md) |
| colorspace | VK_EXT_swapchain_colorspace | Color space extensions, basic rendering, HDR | [vktWsiColorSpaceTests](../testfiles/wsi/vktWsiColorSpaceTests.md) |
| colorspace_compare | VK_EXT_swapchain_colorspace | Color space pixel comparison across formats | [vktWsiColorSpaceTests](../testfiles/wsi/vktWsiColorSpaceTests.md) |
| full_screen_exclusive | VK_EXT_full_screen_exclusive | Full-screen exclusive mode control | [vktWsiFullScreenExclusiveTests](../testfiles/wsi/vktWsiFullScreenExclusiveTests.md) |
| present_id_wait | VK_KHR_present_id / VK_KHR_present_wait | Present ID and wait functionality (v1 and v2) | [vktWsiPresentIdWaitTests](../testfiles/wsi/vktWsiPresentIdWaitTests.md) |
| maintenance1 | VK_KHR_surface_maintenance1 / VK_KHR_swapchain_maintenance1 | Present fence, present modes, scaling, deferred allocation, release images | [vktWsiMaintenance1Tests](../testfiles/wsi/vktWsiMaintenance1Tests.md) |
| present_timing | VK_EXT_present_timing | Present timing with query, time domain, and present-at tests | [vktWsiPresentTimingTests](../testfiles/wsi/vktWsiPresentTimingTests.md) |

### Cross-Platform Groups

| Subgroup | Extension | Description | Level-3 Doc |
|----------|-----------|-------------|-------------|
| display | VK_KHR_display | Display enumeration, mode creation, plane capabilities | [vktWsiDisplayTests](../testfiles/wsi/vktWsiDisplayTests.md) |
| display_control | VK_EXT_display_control | Swapchain counter, display power control, event registration | [vktWsiDisplayControlTests](../testfiles/wsi/vktWsiDisplayControlTests.md) |
| acquire_drm_display | VK_EXT_acquire_drm_display | DRM display acquisition and release | [vktWsiAcquireDrmDisplayTests](../testfiles/wsi/vktWsiAcquireDrmDisplayTests.md) |

### Registration File

[vktWsiTests](../testfiles/wsi/vktWsiTests.md) — root registration/dispatcher file.

## File Inventory

| File | Role | Registers Tests |
|------|------|----------------|
| [vktWsiTests.cpp](../../modules/vulkan/wsi/vktWsiTests.cpp) | Registration | Yes (root group) |
| [vktWsiSurfaceTests.cpp](../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp) | Implementation | Yes |
| [vktWsiSwapchainTests.cpp](../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp) | Implementation | Yes |
| [vktWsiIncrementalPresentTests.cpp](../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp) | Implementation | Yes |
| [vktWsiDisplayTimingTests.cpp](../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp) | Implementation | Yes |
| [vktWsiSharedPresentableImageTests.cpp](../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp) | Implementation | Yes |
| [vktWsiColorSpaceTests.cpp](../../modules/vulkan/wsi/vktWsiColorSpaceTests.cpp) | Implementation | Yes |
| [vktWsiFullScreenExclusiveTests.cpp](../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp) | Implementation | Yes |
| [vktWsiPresentIdWaitTests.cpp](../../modules/vulkan/wsi/vktWsiPresentIdWaitTests.cpp) | Implementation | Yes |
| [vktWsiMaintenance1Tests.cpp](../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp) | Implementation | Yes |
| [vktWsiPresentTimingTests.cpp](../../modules/vulkan/wsi/vktWsiPresentTimingTests.cpp) | Implementation | Yes |
| [vktWsiDisplayTests.cpp](../../modules/vulkan/wsi/vktWsiDisplayTests.cpp) | Implementation | Yes |
| [vktWsiDisplayControlTests.cpp](../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp) | Implementation | Yes |
| [vktWsiAcquireDrmDisplayTests.cpp](../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp) | Implementation | Yes |
| [vktNativeObjectsUtil.cpp](../../modules/vulkan/wsi/vktNativeObjectsUtil.cpp) | Helper utility | No |

## Cross-File Recurring Test Families and Themes

- **Surface query tests**: Multiple files query surface capabilities, formats, and present modes. The surface tests ([vktWsiSurfaceTests](../testfiles/wsi/vktWsiSurfaceTests.md)) provide the foundational query coverage, while other files query surface properties as part of their setup.
- **Rendering stress tests**: Several files render hundreds of frames (typically 300 = 60×5) to verify presentation stability. This pattern appears in incremental_present, shared_presentable_image, display_timing, and maintenance1 tests.
- **Present mode parameterization**: Present modes (FIFO, FIFO_RELAXED, IMMEDIATE, MAILBOX, FIFO_LATEST_READY, SHARED_DEMAND_REFRESH, SHARED_CONTINUOUS_REFRESH) are a common parameter dimension across incremental_present, display_timing, maintenance1, and present_timing tests.
- **OOM simulation**: Both surface and swapchain tests include OOM simulation variants that iterate allocation counts and verify eventual success.

## Cross-File Recurring Parameter Dimensions

| Dimension | Values | Files |
|-----------|--------|-------|
| WSI platform type | xlib, xcb, wayland, android, win32, metal, headless, direct_drm, direct | All per-platform files |
| Present mode | FIFO, FIFO_RELAXED, IMMEDIATE, MAILBOX, FIFO_LATEST_READY, SHARED_DEMAND_REFRESH, SHARED_CONTINUOUS_REFRESH | incremental_present, display_timing, maintenance1, present_timing |
| Surface transform | 9 VkSurfaceTransformFlagsKHR values | incremental_present, shared_presentable_image |
| Composite alpha | 4 values (OPAQUE, PRE_MULTIPLIED, POST_MULTIPLIED, INHERIT) | incremental_present, shared_presentable_image |
| Scaling | NONE, UP, DOWN | incremental_present, shared_presentable_image, maintenance1 |
| Time domain | Up to 6 values | present_timing |

## Cross-File Recurring Support Requirements

| Requirement | Scope | Files |
|-------------|-------|-------|
| VK_KHR_surface + platform surface extension | All per-platform tests | All per-platform files |
| VK_KHR_swapchain | Most per-platform tests | swapchain, incremental_present, display_timing, shared_presentable_image, full_screen_exclusive, present_id_wait, maintenance1, present_timing |
| VK_KHR_get_surface_capabilities2 | Tests using KHR2/EXT2 queries | surface, shared_presentable_image, present_id_wait (v2), present_timing |
| VK_EXT_swapchain_colorspace | Color space tests | colorspace |
| VK_KHR_display | Display-related tests | display, display_control, acquire_drm_display |
| Platform property gating | Conditional test registration | surface (FEATURE_INITIAL_WINDOW_SIZE, FEATURE_RESIZE_WINDOW), incremental_present (SWAPCHAIN_EXTENT_SCALED_TO_WINDOW_SIZE) |

## Cross-File Recurring Verification Methods

| Method | Description | Files |
|--------|-------------|-------|
| API call success | Verify Vulkan calls return VK_SUCCESS or expected result codes | surface, swapchain, display, display_control, acquire_drm_display, full_screen_exclusive |
| Cross-query consistency | Compare results between KHR and KHR2/EXT variants | surface |
| Struct field validation | Validate returned struct fields are within valid ranges | surface, display |
| Rendering loop success | Render hundreds of frames, pass if no Vulkan errors | swapchain, incremental_present, shared_presentable_image, display_timing, maintenance1 |
| OOM simulation | Iterate allocation counts, verify eventual success | surface, swapchain |
| Guard byte / canary | Pre-fill buffers with sentinel values, verify driver did not overwrite past expected bounds | surface (device group), display |
| Result code check | Verify specific VkResult values (VK_INCOMPLETE, VK_NOT_READY, VK_TIMEOUT, etc.) | swapchain, display |
| Timing validation | Verify presentation timing monotonicity and consistency | display_timing, present_timing |
| Fence signal ordering | Poll fence status to verify signal ordering | maintenance1 |
| Pixel comparison | Read back and compare pixel values | colorspace (colorspace_compare only) |

## Notes

- The WSI category does not have a dedicated section in the test specification; documentation is derived from inspected source code.
- The `vktNativeObjectsUtil.cpp` helper provides native window/display creation utilities but does not register tests, so it does not have a Level-3 page.
- The `vkWsiUtil.hpp` framework utility provides shared helpers (InstanceHelper, DeviceHelper, WsiTriangleRenderer) used across multiple test files.
- Per-platform test groups are structurally identical; the "headless" platform is used as the representative in Level-3 documentation.
- The `acquire_drm_display` group is DRM-specific and conditionally compiled (`DEQP_SUPPORT_DRM`); it does not take a `wsiType` parameter.
