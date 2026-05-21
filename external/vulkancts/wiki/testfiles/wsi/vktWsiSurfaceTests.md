# vktWsiSurfaceTests

## Overview

This file implements tests for `VkSurfaceKHR` creation, destruction, and property queries. It covers basic surface lifecycle, custom allocators, OOM simulation, and all standard surface queries (capabilities, formats, present modes) including their extended variants (KHR2, EXT) and device-group versions. Surfaceless query tests are also included for platforms supporting `VK_GOOGLE_surfaceless_query`.

## Role

Implementation file — contains test case implementations and the `createSurfaceTests` registration function.

## Source

[vktWsiSurfaceTests.cpp](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp)

## Registration Hierarchy

```text
wsi.headless.surface
├── create
├── create_custom_allocator
├── create_simulate_oom
├── query_support
├── query_presentation_support
├── query_capabilities
├── query_capabilities2
├── query_protected_capabilities
├── query_surface_counters
├── query_formats
├── query_formats2
├── query_present_modes
├── query_present_modes2
├── query_devgroup_present_capabilities
├── query_devgroup_present_modes
├── destroy_null_handle
├── query_formats_surfaceless
├── query_present_modes_surfaceless
├── query_present_modes2_surfaceless
└── query_formats2_surfaceless
```

> **Conditionally registered children:** The `initial_size` and `resize` tests are only registered when the platform's `PlatformProperties::features` include `FEATURE_INITIAL_WINDOW_SIZE` and `FEATURE_RESIZE_WINDOW` respectively ([vktWsiSurfaceTests.cpp#L1732-L1738](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1732-L1738)). These features are not set for the headless platform, so `initial_size` and `resize` do not appear under `wsi.headless.surface`.

> **Per-Platform Note:** The Level-3 root path uses "headless" as the representative platform. The same structure is replicated for all 9 WSI platform types (e.g., `wsi.xcb.surface`, `wsi.wayland.surface`, `wsi.android.surface`, etc.).

## Test Families

- **create** — Verifies that `vkCreateXXXSurfaceKHR` succeeds and returns a valid `VkSurfaceKHR` handle for the current platform. Creates a WSI instance and native window, then calls `createSurface` and checks the result ([vktWsiSurfaceTests.cpp#L223-L231](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L223-L231)).

- **create_custom_allocator** — Creates a surface using custom allocation callbacks and validates that the allocator is invoked correctly during both creation and cleanup. Verifies that allocation scopes are limited to `OBJECT` and `INSTANCE`, and that no allocations remain after destruction ([vktWsiSurfaceTests.cpp#L272-L296](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L272-L296)).

- **create_simulate_oom** — Simulates out-of-memory conditions during surface creation using a `DeterministicFailAllocator`. Iterates over increasing numbers of allowed allocations (0-1024) until surface creation succeeds, validating that allocation callbacks are used correctly and no leaks occur ([vktWsiSurfaceTests.cpp#L298-L351](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L298-L351)).

- **query_support** — Queries whether each physical device's queue families support presentation to the surface via `vkGetPhysicalDeviceSurfaceSupportKHR`. On Android, asserts that all devices and queue families must support the surface ([vktWsiSurfaceTests.cpp#L362-L395](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L362-L395)).

- **query_presentation_support** — Queries native presentation support via platform-specific `vkGetPhysicalDevicePresentationSupportXXX` and cross-validates against `vkGetPhysicalDeviceSurfaceSupportKHR`. Not supported for `TYPE_DIRECT_DRM` and `TYPE_DIRECT` (throws `NotSupportedError`) ([vktWsiSurfaceTests.cpp#L397-L442](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L397-L442)).

- **query_capabilities** — Queries `VkSurfaceCapabilitiesKHR` via `vkGetPhysicalDeviceSurfaceCapabilitiesKHR` and validates returned values: `minImageCount > 0`, extent bounds consistency, `maxImageArrayLayers > 0`, `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT` set, valid transforms, and at least one composite alpha mode ([vktWsiSurfaceTests.cpp#L499-L525](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L499-L525)).

- **query_capabilities2** — Queries extended surface capabilities via `vkGetPhysicalDeviceSurfaceCapabilities2KHR` (requires `VK_KHR_get_surface_capabilities2`) and cross-validates results against the base KHR1 query. Also verifies that the driver does not modify input structs or `sType`/`pNext` fields ([vktWsiSurfaceTests.cpp#L527-L578](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L527-L578)).

- **query_protected_capabilities** — Queries `VkSurfaceProtectedCapabilitiesKHR` via the pNext chain of `VkSurfaceCapabilities2KHR` (requires `VK_KHR_get_surface_capabilities2` + `VK_KHR_surface_protected_capabilities`). Validates that `supportsProtected` is either 0 or 1 and that the driver does not modify input/output struct fields ([vktWsiSurfaceTests.cpp#L580-L638](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L580-L638)).

- **query_surface_counters** — Queries surface counters via `vkGetPhysicalDeviceSurfaceCapabilities2EXT` (requires `VK_EXT_display_surface_counter`). Cross-validates `VkSurfaceCapabilities2EXT` against `VkSurfaceCapabilitiesKHR`. Verifies that `supportedSurfaceCounters` is zero for non-display surfaces ([vktWsiSurfaceTests.cpp#L233-L270](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L233-L270)).

- **query_formats** — Queries surface formats via `vkGetPhysicalDeviceSurfaceFormatsKHR`. Validates format count consistency between two calls, checks for required formats on Android (R8G8B8A8_UNORM, R8G8B8A8_SRGB, R5G6B5_UNORM_PACK16), checks for duplicate entries, and verifies `VK_INCOMPLETE` is returned when the buffer is too small ([vktWsiSurfaceTests.cpp#L672-L721](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L672-L721)).

- **query_formats2** — Queries extended surface formats via `vkGetPhysicalDeviceSurfaceFormats2KHR` (requires `VK_KHR_get_surface_capabilities2`). Cross-validates against the base format query, checks `sType`/`pNext` integrity, and verifies `VK_INCOMPLETE` behavior with undersized buffers ([vktWsiSurfaceTests.cpp#L781-L878](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L781-L878)).

- **query_present_modes** — Queries present modes via `vkGetPhysicalDeviceSurfacePresentModesKHR`. Validates mode count consistency, checks that `VK_PRESENT_MODE_FIFO_KHR` is always present (and `VK_PRESENT_MODE_MAILBOX_KHR` on Android), and verifies `VK_INCOMPLETE` behavior ([vktWsiSurfaceTests.cpp#L1123-L1172](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1123-L1172)).

- **query_present_modes2** — Queries extended present modes via `vkGetPhysicalDeviceSurfacePresentModes2EXT` (requires `VK_EXT_full_screen_exclusive`). Cross-validates against the base present mode query and verifies `VK_INCOMPLETE` behavior ([vktWsiSurfaceTests.cpp#L890-L966](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L890-L966)).

- **query_devgroup_present_capabilities** — Queries device group present capabilities via `vkGetDeviceGroupPresentCapabilitiesKHR` (requires `VK_KHR_device_group_creation` + `VK_KHR_device_group`). Validates present masks (each device can present on itself), checks that `VK_DEVICE_GROUP_PRESENT_MODE_LOCAL_BIT_KHR` is set, and uses a guard byte pattern to detect buffer overwrites ([vktWsiSurfaceTests.cpp#L1309-L1411](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1309-L1411)).

- **query_devgroup_present_modes** — Queries device group present modes via `vkGetDeviceGroupSurfacePresentModesKHR` and optionally `vkGetPhysicalDevicePresentRectanglesKHR`. Validates mode flags, checks for overlapping present rectangles, and verifies `VK_INCOMPLETE` behavior. Uses guard byte patterns for overflow detection ([vktWsiSurfaceTests.cpp#L1413-L1576](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1413-L1576)).

- **destroy_null_handle** — Verifies that `vkDestroySurfaceKHR` with `VK_NULL_HANDLE` is a valid no-op per the Vulkan specification, both with default and custom allocators. Confirms no allocations or frees occur ([vktWsiSurfaceTests.cpp#L1671-L1690](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1671-L1690)).

- **query_formats_surfaceless** — Queries surface formats without a surface object (using `VK_NULL_HANDLE`) via `VK_GOOGLE_surfaceless_query` and cross-validates against the results obtained with a real surface ([vktWsiSurfaceTests.cpp#L723-L779](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L723-L779)).

- **query_present_modes_surfaceless** — Queries present modes without a surface object using `VK_GOOGLE_surfaceless_query`. Handles both deprecated (spec version 1) and current (spec version >= 2) behavior. Validates that returned modes are among the expected set (`FIFO`, `SHARED_DEMAND_REFRESH`, `SHARED_CONTINUOUS_REFRESH`) ([vktWsiSurfaceTests.cpp#L1248-L1307](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1248-L1307)).

- **query_present_modes2_surfaceless** — Queries extended present modes without a surface object via `vkGetPhysicalDeviceSurfacePresentModes2EXT` with a null surface. Requires `VK_GOOGLE_surfaceless_query` spec version >= 2 and `VK_EXT_full_screen_exclusive` ([vktWsiSurfaceTests.cpp#L968-L1051](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L968-L1051)).

- **query_formats2_surfaceless** — Queries extended surface formats without a surface object via `vkGetPhysicalDeviceSurfaceFormats2KHR` with a null surface. Requires `VK_KHR_get_surface_capabilities2` + `VK_GOOGLE_surfaceless_query`. Cross-validates null-surface results against real-surface results ([vktWsiSurfaceTests.cpp#L1053-L1121](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1053-L1121)).

### Conditionally Registered Test Families

- **initial_size** — (Conditional: `FEATURE_INITIAL_WINDOW_SIZE`) Creates a surface with specific initial window sizes (64x64, 124x119, 256x512) and verifies that `currentExtent` in surface capabilities matches the requested size. Not registered for platforms that lack `FEATURE_INITIAL_WINDOW_SIZE` ([vktWsiSurfaceTests.cpp#L1578-L1617](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1578-L1617)).

- **resize** — (Conditional: `FEATURE_RESIZE_WINDOW`) Resizes the native window to multiple sizes (64x64, 124x119, 256x512) and verifies that `currentExtent` in surface capabilities reflects the new size after each resize. Not registered for platforms that lack `FEATURE_RESIZE_WINDOW` ([vktWsiSurfaceTests.cpp#L1619-L1669](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1619-L1669)).

## Parameter Dimensions

| Dimension | Values | Description |
|-----------|--------|-------------|
| WSI platform type | xlib, xcb, wayland, android, win32, metal, headless, direct_drm, direct | Passed as `vk::wsi::Type` to each test function; determines which platform-specific surface creation API is used |
| Initial window sizes | (64, 64), (124, 119), (256, 512) | Used by `initial_size` and `resize` tests to verify surface extent tracking |

## Support / Feature Requirements

- **Instance extension:** `VK_KHR_surface` (required for all tests)
- **Instance extension:** Platform-specific surface extension (e.g., `VK_KHR_android_surface`, `VK_KHR_xcb_surface`, etc.) — required for all tests
- **Instance extension:** `VK_KHR_display` — required for display surface types
- **Instance extension:** `VK_KHR_get_surface_capabilities2` — required for `query_capabilities2`, `query_formats2`, `query_formats2_surfaceless`
- **Instance extension:** `VK_KHR_surface_protected_capabilities` — required for `query_protected_capabilities`
- **Instance extension:** `VK_GOOGLE_surfaceless_query` — required for `query_formats_surfaceless`, `query_present_modes_surfaceless`, `query_present_modes2_surfaceless`, `query_formats2_surfaceless`
- **Instance extension:** `VK_KHR_device_group_creation` — required for `query_devgroup_present_capabilities`, `query_devgroup_present_modes`
- **Instance extension:** `VK_EXT_display_surface_counter` — required for `query_surface_counters`
- **Device extension:** `VK_EXT_full_screen_exclusive` — required for `query_present_modes2`, `query_present_modes2_surfaceless`
- **Device extension:** `VK_KHR_device_group` — required for `query_devgroup_present_capabilities`, `query_devgroup_present_modes`
- **Device extension:** `VK_KHR_swapchain` — required for `query_devgroup_present_capabilities`, `query_devgroup_present_modes`
- **Platform feature:** `FEATURE_INITIAL_WINDOW_SIZE` — required for `initial_size`
- **Platform feature:** `FEATURE_RESIZE_WINDOW` — required for `resize`
- **Platform restriction:** `query_presentation_support` throws `NotSupportedError` for `TYPE_DIRECT_DRM` and `TYPE_DIRECT`

## Verification Methods

- **API call success verification:** Tests verify that surface creation, destruction, and query calls return `VK_SUCCESS` or the expected result code (e.g., `VK_INCOMPLETE`).
- **Cross-query consistency:** Extended queries (KHR2, EXT) are cross-validated against their base KHR1 counterparts to ensure the same information is reported.
- **Struct validation:** Returned capability, format, and present mode structures are checked for valid enum values and sensible bounds (e.g., `minImageCount > 0`, extents within range, `currentTransform` is a single bit).
- **VK_INCOMPLETE verification:** Several query tests supply an undersized buffer and verify that `VK_INCOMPLETE` is returned and that the driver does not write past the reported count.
- **Guard byte pattern:** Device group tests place a guard byte pattern (`0xcd`) after the output struct to detect buffer overwrites by the driver.
- **OOM simulation:** `create_simulate_oom` uses a `DeterministicFailAllocator` to inject allocation failures and verifies no memory leaks occur via `AllocationCallbackRecorder` validation.
- **Allocation callback validation:** `create_custom_allocator` verifies that the custom allocator is invoked during surface creation and that no allocations remain after destruction.
- **No-op verification:** `destroy_null_handle` confirms that destroying a null surface handle does not crash, produce errors, or trigger allocations.
- **Input struct immutability:** `query_capabilities2` and `query_protected_capabilities` verify that the driver does not modify input structs (`VkPhysicalDeviceSurfaceInfo2KHR`).

## Notes / Uncertainties

- All tests are registered as free functions via `addFunctionCase()` — there are no `checkSupport()` methods. Support checks are performed inline via `TCU_THROW(NotSupportedError)` when required extensions or features are unavailable.
- The `initial_size` and `resize` tests are conditionally registered based on `PlatformProperties::features` flags ([vktWsiSurfaceTests.cpp#L1732-L1738](../../../modules/vulkan/wsi/vktWsiSurfaceTests.cpp#L1732-L1738)), so they may not appear on all platforms. For the headless platform specifically, these features are not set.
- Surfaceless query tests rely on `VK_GOOGLE_surfaceless_query`, which is a vendor-specific extension and may not be available on all implementations. The `query_present_modes_surfaceless` test has version-dependent behavior: spec version 1 uses deprecated cross-validation logic, while spec version >= 2 validates against a fixed set of valid present modes.
- The `query_surface_counters` test also requires `VK_KHR_display` as an instance extension in addition to `VK_EXT_display_surface_counter`.
- The `query_present_modes2` test requires `VK_EXT_full_screen_exclusive` at the device level and will throw `NotSupportedError` if unavailable.
