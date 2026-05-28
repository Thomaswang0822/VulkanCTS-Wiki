# vktWsiDisplayControlTests

## Overview

Tests for the `VK_EXT_display_control` extension, which provides mechanisms to control display power state, register display and device events, and query swapchain surface counters. These tests operate on direct display surfaces (VK_KHR_display) rather than platform window systems, and verify that the extension's commands return valid results and that surface counters reflect expected frame presentation counts.

## Role of file

Implementation file. Contains all test case definitions, test instance logic, and the registration function for the `wsi.display_control` test group.

## Source code

[vktWsiDisplayControlTests.cpp](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp)

## Registration Hierarchy

```text
wsi.display_control
├── swapchain_counter
├── display_power_control
├── register_display_event
└── register_device_event
```

## Test Families

### swapchain_counter

A `SwapchainCounterTestCase` that creates a full rendering loop on a direct display surface with a swapchain configured with `VkSwapchainCounterCreateInfoEXT` enabling `VK_SURFACE_COUNTER_VBLANK_EXT`. The test instance ([SwapchainCounterTestInstance](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L543-L602)) renders 20 frames in `VK_PRESENT_MODE_FIFO_KHR` mode, then calls `vkGetSwapchainCounterEXT` to verify that the vblank counter value is within the expected range (between `frameCount - swapchainImageCount` and `frameCount`). Handles `VK_ERROR_OUT_OF_DATE_KHR` by recreating swapchain resources up to a maximum of 10 times.

Source: [vktWsiDisplayControlTests.cpp#L990](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L990)

### display_power_control

A function test case that calls `vkDisplayPowerControlEXT` on each available display, cycling through a sequence of power states: ON, SUSPEND, OFF, and back to ON, with a 1000 ms sleep between each transition. Verifies that each call returns `VK_SUCCESS`.

Source: [vktWsiDisplayControlTests.cpp#L991](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L991), test logic at [testDisplayPowerControl](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L889-L930)

### register_display_event

A function test case that calls `vkRegisterDisplayEventEXT` with event type `VK_DISPLAY_EVENT_TYPE_FIRST_PIXEL_OUT_EXT` for each available display, obtaining a fence for each. Verifies that each call returns `VK_SUCCESS`, then destroys the fences.

Source: [vktWsiDisplayControlTests.cpp#L992](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L992), test logic at [testDisplayEvent](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L932-L962)

### register_device_event

A function test case that calls `vkRegisterDeviceEventEXT` with event type `VK_DEVICE_EVENT_TYPE_DISPLAY_HOTPLUG_EXT`, obtaining a fence. Verifies that the call returns `VK_SUCCESS`, then destroys the fence.

Source: [vktWsiDisplayControlTests.cpp#L993](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L993), test logic at [testDeviceEvent](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L964-L984)

## Parameter Dimensions

These tests do not take a `wsiType` parameter. All tests operate on direct display surfaces (`VK_KHR_display`) rather than platform-specific window systems.

- **swapchain_counter**: Uses `VK_PRESENT_MODE_FIFO_KHR` as the fixed present mode. Frame count is hardcoded to 20. Maximum out-of-date retry count is 10.
- **display_power_control**: Cycles through a fixed sequence of 4 power states (ON, SUSPEND, OFF, ON) with 1000 ms waits.
- **register_display_event**: Uses `VK_DISPLAY_EVENT_TYPE_FIRST_PIXEL_OUT_EXT` as the fixed event type.
- **register_device_event**: Uses `VK_DEVICE_EVENT_TYPE_DISPLAY_HOTPLUG_EXT` as the fixed event type.

## Support / Feature Requirements

- **VK_EXT_display_control**: Required by all tests. Checked via `context.requireDeviceFunctionality("VK_EXT_display_control")` in [checkSupport](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L847-L851) and at the start of each function test case.
- **VK_KHR_display**: Required by all tests. Checked via `context.requireInstanceFunctionality("VK_KHR_display")` in the swapchain_counter checkSupport, and implicitly required by the direct display surface creation in other tests.
- **VK_KHR_surface**: Required instance extension for swapchain_counter (enabled during custom instance creation at [createInstance](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L70-L79)).
- **VK_EXT_display_surface_counter**: Required instance extension for swapchain_counter (enabled during custom instance creation).
- **VK_KHR_swapchain**: Required device extension for swapchain_counter (enabled during custom device creation at [createTestDevice](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L96-L144)).
- **VK_SURFACE_COUNTER_VBLANK_EXT**: Must be supported by the surface for swapchain_counter (checked at [createSwapchainConfig](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L478-L479)).
- **Direct display availability**: All tests require that no windowing system has claimed the display (checked via `platform.hasDisplay()` at [createTestDevice](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L130-L138) and [getDisplays](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L868-L875)).
- **At least one VkDisplayKHR**: Must be available and intersecting with a display plane (checked at [getDisplayAndDisplayPlane](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L146-L187) and [getDisplays](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L853-L887)).

## Verification Methods

- **Counter value range check** (swapchain_counter): After rendering all frames, `vkGetSwapchainCounterEXT` is called with `VK_SURFACE_COUNTER_VBLANK_EXT`. The returned counter must satisfy `frameCount - swapchainImageCount <= counter <= frameCount`. Failure is reported via `tcu::ResultCollector` as "Invalid surface counter value". See [render](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L750-L759).
- **Return code validation** (display_power_control, register_display_event, register_device_event): Each Vulkan command call is checked for `VK_SUCCESS`. A non-success result causes an immediate test failure with a descriptive message.
- **Swapchain out-of-date handling** (swapchain_counter): `VK_ERROR_OUT_OF_DATE_KHR` errors trigger resource recreation up to 10 times; exceeding this limit results in test failure.

## Notes/Uncertainties

- These tests require a physical display connected and not claimed by a windowing system, making them unsuitable for headless CI environments without special display infrastructure.
- The `register_display_event` and `register_device_event` tests only verify that the registration calls succeed and fences are created; they do not wait on the fences or verify that the events actually fire.
- The `display_power_control` test changes display power states including OFF, which may render the display temporarily unavailable. The 1000 ms sleep between transitions is intended to allow recovery, but timing may vary across hardware.
- The `swapchain_counter` test uses a custom instance and device creation path (via `createCustomInstanceWithExtensions` and `createCustomDevice`) rather than the default context device, because it needs to enable specific display-related extensions.
- The counter validation in `swapchain_counter` uses a range rather than an exact value because some swapchain images may not have been presented yet at the time of the check.
