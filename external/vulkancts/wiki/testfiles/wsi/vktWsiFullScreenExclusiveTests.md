# vktWsiFullScreenExclusiveTests

## Overview

Tests for the `VK_EXT_full_screen_exclusive` extension, which provides applications with control over full-screen exclusive mode on swapchains. The tests create a swapchain with a specific full-screen exclusive policy, render 60 frames using a triangle renderer, and verify that the full-screen exclusive mode is correctly acquired, held, and (where applicable) released without errors.

## Role of file

Implementation file. Contains the test case registration logic and the full test implementation for `VK_EXT_full_screen_exclusive` WSI tests.

## Source code

[vktWsiFullScreenExclusiveTests.cpp](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp)

## Registration Hierarchy

```text
wsi.headless.full_screen_exclusive
├── default
├── allowed
├── disallowed
└── application_controlled
```

## Test Families

### default

Tests swapchain creation and rendering with `VK_FULL_SCREEN_EXCLUSIVE_DEFAULT_EXT`. The implementation chooses the full-screen exclusive policy. Defined at [vktWsiFullScreenExclusiveTests.cpp#L627](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L627).

### allowed

Tests swapchain creation and rendering with `VK_FULL_SCREEN_EXCLUSIVE_ALLOWED_EXT`. The implementation is permitted to use full-screen exclusive mode if available. Defined at [vktWsiFullScreenExclusiveTests.cpp#L628](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L628).

### disallowed

Tests swapchain creation and rendering with `VK_FULL_SCREEN_EXCLUSIVE_DISALLOWED_EXT`. The implementation must not use full-screen exclusive mode. Defined at [vktWsiFullScreenExclusiveTests.cpp#L629](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L629).

### application_controlled

Tests swapchain creation and rendering with `VK_FULL_SCREEN_EXCLUSIVE_APPLICATION_CONTROLLED_EXT`. The application explicitly acquires and releases full-screen exclusive mode via `vkAcquireFullScreenExclusiveModeEXT` and `vkReleaseFullScreenExclusiveModeEXT`. This is the only mode where the test actively calls acquire/release. Defined at [vktWsiFullScreenExclusiveTests.cpp#L630](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L630).

## Parameter Dimensions

| Parameter | Type | Values | Description |
|-----------|------|--------|-------------|
| `wsiType` | `vk::wsi::Type` | Per-platform (e.g. headless) | WSI platform type, inherited from the parent group registration |
| `fseType` | `VkFullScreenExclusiveEXT` | `DEFAULT`, `ALLOWED`, `DISALLOWED`, `APPLICATION_CONTROLLED` | Full-screen exclusive policy applied to the swapchain |

Each test case is parameterized by both `wsiType` (set by the per-platform parent group) and one `fseType` value. The `fseType` determines the test name within the group.

## Support/Feature Requirements

- **VK_EXT_full_screen_exclusive**: Required at the device level. The test checks for this extension on the device at runtime and throws `NotSupportedError` if absent ([vktWsiFullScreenExclusiveTests.cpp#L306-L308](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L306-L308), [vktWsiFullScreenExclusiveTests.cpp#L318-L319](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L318-L319)). This is a device extension, not an instance extension.
- **VK_KHR_surface**: Required for instance creation.
- **VK_KHR_swapchain**: Required for device creation.
- **VK_KHR_get_surface_capabilities2**: Enabled if supported; used to query `VkSurfaceCapabilities2KHR` with the full-screen exclusive pNext chain.
- **VK_KHR_display**: Enabled if the WSI type is a display surface.
- **VkSurfaceCapabilitiesFullScreenExclusiveEXT::fullScreenExclusiveSupported**: Must be `VK_TRUE` on the surface; otherwise the test throws `NotSupportedError` ([vktWsiFullScreenExclusiveTests.cpp#L379-L381](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L379-L381)).
- On Win32 platforms, `VkSurfaceFullScreenExclusiveWin32InfoEXT` with an `HMONITOR` value is chained into the surface info and swapchain creation.

## Verification Methods

- **Swapchain creation**: The swapchain is created with the `VkSurfaceFullScreenExclusiveInfoEXT` structure chained via `pNext`. For `APPLICATION_CONTROLLED` mode, a `VK_ERROR_INITIALIZATION_FAILED` result from swapchain creation is treated as a quality warning rather than a hard failure, per the spec allowance that exclusive full-screen access may be unavailable ([vktWsiFullScreenExclusiveTests.cpp#L409-L418](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L409-L418)).
- **Full-screen exclusive acquire/release**: For `APPLICATION_CONTROLLED` mode, `vkAcquireFullScreenExclusiveModeEXT` is called before rendering frames, and `vkReleaseFullScreenExclusiveModeEXT` is called after rendering completes. Results of `VK_ERROR_INITIALIZATION_FAILED` and `VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT` are handled gracefully ([vktWsiFullScreenExclusiveTests.cpp#L468-L494](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L468-L494), [vktWsiFullScreenExclusiveTests.cpp#L576-L589](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L576-L589)).
- **Rendering loop**: 60 frames are rendered using `WsiTriangleRenderer`. Each frame acquires a swapchain image, records rendering, submits, and presents. `VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT` from `vkAcquireNextImageKHR` or `vkQueuePresentKHR` is logged and tracked but does not cause a hard failure ([vktWsiFullScreenExclusiveTests.cpp#L508-L517](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L508-L517), [vktWsiFullScreenExclusiveTests.cpp#L549-L558](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L549-L558)).
- **Result evaluation**: Pass if full-screen exclusive was acquired and not lost. Quality warning if exclusive was lost during the test, or if exclusive mode could not be acquired. The test also returns a quality warning for `APPLICATION_CONTROLLED` if the window was not in the foreground ([vktWsiFullScreenExclusiveTests.cpp#L593-L610](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L593-L610)).

## Notes/Uncertainties

- The test uses a full-screen-sized window (`getFullScreenSize`) rather than a small window, which may affect behavior on platforms where full-screen exclusive mode depends on window size matching the display.
- On Win32, the test attempts to bring the window to the foreground via `setForeground()`. If this fails, the `APPLICATION_CONTROLLED` test returns a quality warning rather than a pass, since exclusive full-screen access may require the window to be in the foreground.
- The `VK_EXT_full_screen_exclusive` extension is only conditionally added to the device extension list (only if supported), but the test itself will throw `NotSupportedError` if the extension is not present, so tests will be skipped on devices that do not support it.
- The test does not verify rendering correctness (pixel values); it only verifies that the swapchain lifecycle and full-screen exclusive mode transitions complete without unexpected errors.
