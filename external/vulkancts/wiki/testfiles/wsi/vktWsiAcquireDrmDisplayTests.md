# vktWsiAcquireDrmDisplayTests

## Overview

This file implements Vulkan conformance tests for the `VK_EXT_acquire_drm_display` extension, which provides an interface between Vulkan and the Linux DRM (Direct Rendering Manager) subsystem. The tests cover the `vkGetDrmDisplayEXT`, `vkAcquireDrmDisplayEXT`, and `vkReleaseDisplayEXT` entry points, exercising both success paths and error conditions for each function.

## Role of File

Implementation file. Contains the `AcquireDrmDisplayTestInstance` class that executes DRM display operations, the `AcquireDrmDisplayTestsCase` test case class, and the `createAcquireDrmDisplayTests` registration function that populates the test group.

## Source Code

[vktWsiAcquireDrmDisplayTests.cpp](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp)

## Registration Hierarchy

```text
wsi.acquire_drm_display
├── get_drm_display
├── get_drm_display_invalid_fd
├── get_drm_display_invalid_connector_id
├── get_drm_display_not_master
├── get_drm_display_unowned_connector_id
├── acquire_drm_display
├── acquire_drm_display_invalid_fd
├── acquire_drm_display_not_master
├── acquire_drm_display_unowned_connector_id
└── release_display
```

## Test Families

### get_drm_display

Success-path test for `vkGetDrmDisplayEXT`. Opens a DRM fd, finds a connected connector, and calls `vkGetDrmDisplayEXT` with valid parameters. Verifies that the call returns `VK_SUCCESS` and that the output `VkDisplayKHR` handle is set to a valid (non-null, non-sentinel) value. Does not require DRM master permissions.

### get_drm_display_invalid_fd

Error-path test for `vkGetDrmDisplayEXT`. Calls the function with an invalid file descriptor (opened on `/` with `O_RDONLY | O_PATH` instead of a DRM device). Verifies that the result is `VK_ERROR_UNKNOWN`.

### get_drm_display_invalid_connector_id

Error-path test for `vkGetDrmDisplayEXT`. Calls the function with a fabricated connector ID (valid connector ID + 1234). Verifies that the result is `VK_ERROR_UNKNOWN` and that the output display handle is `VK_NULL_HANDLE`.

### get_drm_display_not_master

Success-path test for `vkGetDrmDisplayEXT` when the caller does not hold DRM master permissions. Opens two DRM file descriptors so the second one is not the master, then calls `vkGetDrmDisplayEXT` with the non-master fd. Verifies that the call still returns `VK_SUCCESS` with a valid display handle. This confirms that `vkGetDrmDisplayEXT` does not require master permissions.

### get_drm_display_unowned_connector_id

Error-path test for `vkGetDrmDisplayEXT`. Creates a DRM lease for one connector, then attempts to get the display for a different (unowned) connector using the leased fd. Verifies that the result is `VK_ERROR_UNKNOWN` and the display handle is `VK_NULL_HANDLE`. Requires DRM master permissions and two physically connected displays.

### acquire_drm_display

Success-path test for `vkAcquireDrmDisplayEXT`. First obtains a valid `VkDisplayKHR` via `vkGetDrmDisplayEXT`, then acquires it with `vkAcquireDrmDisplayEXT`. Verifies both calls return `VK_SUCCESS`. Requires DRM master permissions.

### acquire_drm_display_invalid_fd

Error-path test for `vkAcquireDrmDisplayEXT`. Obtains a valid display handle using a correct DRM fd, then attempts to acquire the display using an invalid fd (opened on `/`). Verifies that `vkAcquireDrmDisplayEXT` returns `VK_ERROR_UNKNOWN`.

### acquire_drm_display_not_master

Error-path test for `vkAcquireDrmDisplayEXT`. Obtains a valid display handle, then attempts to acquire it using a non-master DRM fd. Verifies that `vkAcquireDrmDisplayEXT` returns `VK_ERROR_INITIALIZATION_FAILED`.

### acquire_drm_display_unowned_connector_id

Error-path test for `vkAcquireDrmDisplayEXT`. Creates a DRM lease for one connector, obtains the display for a different (unowned) connector using the master fd, then attempts to acquire that display using the leased fd. Verifies that `vkAcquireDrmDisplayEXT` returns `VK_ERROR_INITIALIZATION_FAILED`. Requires DRM master permissions and two physically connected displays.

### release_display

Success-path test for `vkReleaseDisplayEXT` (from `VK_EXT_display_control` / `VK_EXT_direct_mode_display`). Acquires a DRM display via `vkGetDrmDisplayEXT` and `vkAcquireDrmDisplayEXT`, then releases it with `vkReleaseDisplayEXT`. Verifies all three calls return `VK_SUCCESS`. Requires DRM master permissions.

## Parameter Dimensions

This test group has no parameter dimensions. Each test is a standalone case identified by the `DrmTestIndex` enum, dispatched via a switch statement in the `iterate()` method. The group does not take a `wsiType` parameter.

## Support / Feature Requirements

- **Instance extensions**: `VK_KHR_surface`, `VK_KHR_display`, `VK_EXT_direct_mode_display`, `VK_EXT_acquire_drm_display` (all four are required; the test throws `NotSupportedError` if any are missing) [vktWsiAcquireDrmDisplayTests.cpp#L183-L188](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L183-L188)
- **Compile-time guard**: The entire test body is conditionally compiled under `DEQP_SUPPORT_DRM && !defined(CTS_USES_VULKANSC)`. When DRM is not supported at compile time, `iterate()` unconditionally throws `NotSupportedError` [vktWsiAcquireDrmDisplayTests.cpp#L34-L36](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L34-L36)
- **Runtime DRM requirements**: A DRM primary device node must be discoverable via `VkPhysicalDeviceDrmPropertiesEXT` [vktWsiAcquireDrmDisplayTests.cpp#L218-L219](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L218-L219)
- **DRM master permissions**: Tests `acquire_drm_display`, `acquire_drm_display_not_master` (indirectly), `acquire_drm_display_unowned_connector_id`, `get_drm_display_unowned_connector_id`, and `release_display` require the process to hold DRM master permissions (no other DRM client like X or Wayland running)
- **Multiple connected displays**: Tests `get_drm_display_unowned_connector_id` and `acquire_drm_display_unowned_connector_id` additionally require at least two physically connected DRM connectors

## Verification Methods

- **Return code validation**: Every test checks the `VkResult` returned by the Vulkan entry point against an expected value (`VK_SUCCESS` for success-path tests, `VK_ERROR_UNKNOWN` or `VK_ERROR_INITIALIZATION_FAILED` for error-path tests). Unexpected results trigger `TCU_FAIL`.
- **Output handle validation**: Success-path tests for `vkGetDrmDisplayEXT` verify the output `VkDisplayKHR` is neither `VK_NULL_HANDLE` nor the sentinel `INVALID_DISPLAY` value. Error-path tests verify the handle is set to `VK_NULL_HANDLE`.
- **Extension presence check**: All tests check for `VK_ERROR_EXTENSION_NOT_PRESENT` and convert it to `NotSupportedError` rather than a test failure.
- **DRM resource validation**: Helper methods (`getDrmFdPtr`, `getConnectedConnectorId`, `getValidCrtcId`, `isDrmMaster`) validate DRM environment prerequisites and throw `NotSupportedError` when the runtime environment does not meet requirements.

## Notes / Uncertainties

- The `get_drm_display_not_master` test is a success-path test, not an error test. It verifies that `vkGetDrmDisplayEXT` works even without DRM master permissions, which is a notable behavioral distinction from `vkAcquireDrmDisplayEXT` (which requires master).
- The `release_display` test uses `vkReleaseDisplayEXT`, which belongs to the `VK_EXT_direct_mode_display` extension rather than `VK_EXT_acquire_drm_display`, but it is included in this group because it completes the acquire/release lifecycle.
- Several tests have stringent runtime environment requirements (DRM master, no competing display servers, multiple physical displays) that may cause them to report `NotSupportedError` in typical CI or desktop environments.
- The `INVALID_DISPLAY` sentinel value is defined as `VkDisplayKHR(reinterpret_cast<void*>(0xFFFFFFFF))` and is used solely as a pre-call initialization sentinel to detect whether the output parameter was written [vktWsiAcquireDrmDisplayTests.cpp#L56](../../../modules/vulkan/wsi/vktWsiAcquireDrmDisplayTests.cpp#L56).
