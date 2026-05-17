# vktSynchronizationInternallySynchronizedTests

## Overview

Tests for the `VK_KHR_internally_synchronized_queues` extension, which allows multiple threads to submit work to the same Vulkan queue concurrently without external synchronization. These tests create queues with the `VK_DEVICE_QUEUE_CREATE_INTERNALLY_SYNCHRONIZED_BIT_KHR` flag, spawn multiple threads that each perform different operations on the same queue simultaneously, and verify that all operations complete correctly without data corruption.

This is a **sync2-only** test file (non-SC). It is registered under the `synchronization2` category only. Although the factory function takes a `SynchronizationType` parameter, it is only ever called with `SYNCHRONIZATION2`.

## Role of File

Provides the `internally_synchronized_queues` test group, which validates that internally synchronized queues correctly handle concurrent submissions from multiple threads. Each test spawns 4 threads, each performing a different operation type on the same queue, and verifies that all threads produce correct results without interference.

## Source Code

- [vktSynchronizationInternallySynchronizedTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp)

## Registration Hierarchy

```text
synchronization2.internally_synchronized_queues
├── android_bind_sparse_wsi
├── android_debug_utils_wsi
├── android_device_wait_idle_wsi
├── android_large2_wsi
├── android_out_of_band_wsi
├── android_performance_configuration_wsi
├── android_small2_wsi
├── android_wsi_bind_sparse
├── android_wsi_debug_utils
├── android_wsi_device_wait_idle
├── android_wsi_large2
├── android_wsi_out_of_band
├── android_wsi_performance_configuration
├── android_wsi_small2
├── bind_sparse_bind_sparse
├── bind_sparse_debug_utils
├── bind_sparse_device_wait_idle
├── bind_sparse_large2
├── bind_sparse_out_of_band
├── bind_sparse_performance_configuration
├── bind_sparse_small2
├── debug_utils_bind_sparse
├── debug_utils_debug_utils
├── debug_utils_device_wait_idle
├── debug_utils_large2
├── debug_utils_out_of_band
├── debug_utils_performance_configuration
├── debug_utils_small2
├── device_wait_idle_bind_sparse
├── device_wait_idle_debug_utils
├── device_wait_idle_device_wait_idle
├── device_wait_idle_large2
├── device_wait_idle_out_of_band
├── device_wait_idle_performance_configuration
├── device_wait_idle_small2
├── direct_bind_sparse_wsi
├── direct_debug_utils_wsi
├── direct_device_wait_idle_wsi
├── direct_drm_bind_sparse_wsi
├── direct_drm_debug_utils_wsi
├── direct_drm_device_wait_idle_wsi
├── direct_drm_large2_wsi
├── direct_drm_out_of_band_wsi
├── direct_drm_performance_configuration_wsi
├── direct_drm_small2_wsi
├── direct_drm_wsi_bind_sparse
├── direct_drm_wsi_debug_utils
├── direct_drm_wsi_device_wait_idle
├── direct_drm_wsi_large2
├── direct_drm_wsi_out_of_band
├── direct_drm_wsi_performance_configuration
├── direct_drm_wsi_small2
├── direct_drm_wsi_wsi
├── direct_large2_wsi
├── direct_out_of_band_wsi
├── direct_performance_configuration_wsi
├── direct_small2_wsi
├── direct_wsi_bind_sparse
├── direct_wsi_debug_utils
├── direct_wsi_device_wait_idle
├── direct_wsi_large2
├── direct_wsi_out_of_band
├── direct_wsi_performance_configuration
├── direct_wsi_small2
├── direct_wsi_wsi
├── headless_bind_sparse_wsi
├── headless_debug_utils_wsi
├── headless_device_wait_idle_wsi
├── headless_large2_wsi
├── headless_out_of_band_wsi
├── headless_performance_configuration_wsi
├── headless_small2_wsi
├── headless_wsi_bind_sparse
├── headless_wsi_debug_utils
├── headless_wsi_device_wait_idle
├── headless_wsi_large2
├── headless_wsi_out_of_band
├── headless_wsi_performance_configuration
├── headless_wsi_small2
├── headless_wsi_wsi
├── large2_bind_sparse
├── large2_debug_utils
├── large2_device_wait_idle
├── large2_large2
├── large2_out_of_band
├── large2_performance_configuration
├── large2_small2
├── metal_bind_sparse_wsi
├── metal_debug_utils_wsi
├── metal_device_wait_idle_wsi
├── metal_large2_wsi
├── metal_out_of_band_wsi
├── metal_performance_configuration_wsi
├── metal_small2_wsi
├── metal_wsi_bind_sparse
├── metal_wsi_debug_utils
├── metal_wsi_device_wait_idle
├── metal_wsi_large2
├── metal_wsi_out_of_band
├── metal_wsi_performance_configuration
├── metal_wsi_small2
├── metal_wsi_wsi
├── out_of_band_bind_sparse
├── out_of_band_debug_utils
├── out_of_band_device_wait_idle
├── out_of_band_large2
├── out_of_band_out_of_band
├── out_of_band_performance_configuration
├── out_of_band_small2
├── performance_configuration_bind_sparse
├── performance_configuration_debug_utils
├── performance_configuration_device_wait_idle
├── performance_configuration_large2
├── performance_configuration_out_of_band
├── performance_configuration_performance_configuration
├── performance_configuration_small2
├── small2_bind_sparse
├── small2_debug_utils
├── small2_device_wait_idle
├── small2_large2
├── small2_out_of_band
├── small2_performance_configuration
├── small2_small2
├── wayland_bind_sparse_wsi
├── wayland_debug_utils_wsi
├── wayland_device_wait_idle_wsi
├── wayland_large2_wsi
├── wayland_out_of_band_wsi
├── wayland_performance_configuration_wsi
├── wayland_small2_wsi
├── wayland_wsi_bind_sparse
├── wayland_wsi_debug_utils
├── wayland_wsi_device_wait_idle
├── wayland_wsi_large2
├── wayland_wsi_out_of_band
├── wayland_wsi_performance_configuration
├── wayland_wsi_small2
├── wayland_wsi_wsi
├── win32_bind_sparse_wsi
├── win32_debug_utils_wsi
├── win32_device_wait_idle_wsi
├── win32_large2_wsi
├── win32_out_of_band_wsi
├── win32_performance_configuration_wsi
├── win32_small2_wsi
├── win32_wsi_bind_sparse
├── win32_wsi_debug_utils
├── win32_wsi_device_wait_idle
├── win32_wsi_large2
├── win32_wsi_out_of_band
├── win32_wsi_performance_configuration
├── win32_wsi_small2
├── win32_wsi_wsi
├── xcb_bind_sparse_wsi
├── xcb_debug_utils_wsi
├── xcb_device_wait_idle_wsi
├── xcb_large2_wsi
├── xcb_out_of_band_wsi
├── xcb_performance_configuration_wsi
├── xcb_small2_wsi
├── xcb_wsi_bind_sparse
├── xcb_wsi_debug_utils
├── xcb_wsi_device_wait_idle
├── xcb_wsi_large2
├── xcb_wsi_out_of_band
├── xcb_wsi_performance_configuration
├── xcb_wsi_small2
├── xcb_wsi_wsi
├── xlib_bind_sparse_wsi
├── xlib_debug_utils_wsi
├── xlib_device_wait_idle_wsi
├── xlib_large2_wsi
├── xlib_out_of_band_wsi
├── xlib_performance_configuration_wsi
├── xlib_small2_wsi
├── xlib_wsi_bind_sparse
├── xlib_wsi_debug_utils
├── xlib_wsi_device_wait_idle
├── xlib_wsi_large2
├── xlib_wsi_out_of_band
├── xlib_wsi_performance_configuration
├── xlib_wsi_small2
└── xlib_wsi_wsi
```

Registered in the sync2 path via [`createInternallySynchronizedTests()`](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp#L1656) added to the `synchronization2` group in [vktSynchronizationTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L130).

**NOT registered under `synchronization`** (LEGACY). The LEGACY category has a separate `internally_synchronized_objects` group from a different source file.

### Test Name Generation

Test names follow two patterns depending on whether WSI is involved:

- **Core combinations** (no WSI thread): `<testType3>_<testType4>` -- e.g. `small2_large2`, `bind_sparse_debug_utils`
- **WSI variants** (at least one WSI thread): `<wsiType>_<testType3>_<testType4>` -- e.g. `android_small2_wsi`, `wayland_wsi_bind_sparse`

| TestType | Name | Description |
|----------|------|-------------|
| TYPE_SMALL_IMAGE_SYNC | small | Small image (8x8) draw with legacy queueSubmit |
| TYPE_LARGE_IMAGE_SYNC | large | Large image (4096x4096) draw with legacy queueSubmit |
| TYPE_SMALL_IMAGE_SYNC2 | small2 | Small image draw with queueSubmit2 |
| TYPE_LARGE_IMAGE_SYNC2 | large2 | Large image draw with queueSubmit2 |
| TYPE_QUEUE_BIND_SPARSE | bind_sparse | Sparse buffer/image bind and copy operations |
| TYPE_WSI | wsi | Swapchain acquire, draw, present |
| TYPE_DEBUG_UTILS | debug_utils | Draw with debug utils labels |
| TYPE_PERFORMANCE_CONFIGURATION | performance_configuration | INTEL performance query acquire/configure/submit |
| TYPE_OUT_OF_BAND | out_of_band | NV low latency out-of-band queue notification |
| TYPE_DEVICE_WAIT_IDLE | device_wait_idle | Buffer copy with deviceWaitIdle |

### Thread Assignment

Each test spawns 4 threads with the following test types:
- Thread 1: `TYPE_SMALL_IMAGE_SYNC` (always)
- Thread 2: `TYPE_LARGE_IMAGE_SYNC` (always)
- Thread 3: `tests[i]` (varies per test case)
- Thread 4: `tests[j]` (varies per test case)

Where `tests` = {small2, large2, bind_sparse, wsi, debug_utils, performance_configuration, out_of_band, device_wait_idle}

## Test Families

### internally_synchronized_queues -- Internally synchronized queue concurrent submission tests

All 183 test cases in this group use the same test class `InternallySynchronizedQueuesTestCase`. Each test creates a custom device with internally synchronized queues, spawns 4 concurrent threads each running a different operation on the same queue, and verifies all threads complete successfully.

The test cases are generated as a Cartesian product of the `tests` vector (8 types for threads 3 and 4), yielding 64 combinations. When either thread 3 or thread 4 uses the WSI type, additional per-WSI-platform variants are created (9 WSI types: android, direct, direct_drm, headless, metal, wayland, win32, xcb, xlib). The `android_wsi_wsi` variant is skipped because multiple concurrent WSI windows are not supported on Android.

The 49 core (non-WSI) test cases use the naming pattern `<testType3>_<testType4>`, where both testType3 and testType4 are drawn from the non-WSI subset {small2, large2, bind_sparse, debug_utils, performance_configuration, out_of_band, device_wait_idle}.

The 134 WSI test cases use the naming pattern `<wsiType>_<testType3>_<testType4>`, where at least one of testType3 or testType4 is `wsi`.

## Parameter Dimensions

| Dimension | Values | Notes |
|-----------|--------|-------|
| Test type 3 (thread 3) | 8 types: small2, large2, bind_sparse, wsi, debug_utils, performance_configuration, out_of_band, device_wait_idle | From `tests` vector |
| Test type 4 (thread 4) | 8 types (same as above) | Cartesian product with test type 3 |
| Queue creation type | SINGLE_QUEUE, FIRST_INTERN_SYNCED, LAST_INTERN_SYNCED, TWO_INTERN_SYNCED_USE_FIRST, TWO_INTERN_SYNCED_USE_LAST | Selected via `(i + j) % queueCreation.size()` |
| Same queue family | true/false | Alternates based on `i % 2 == 0` |
| WSI type | All `vk::wsi::Type` values | Only when WSI test type is involved |

## Support/Feature Requirements

| Requirement | Type | Notes |
|-------------|------|-------|
| VK_KHR_internally_synchronized_queues | Device Extension | Required for all tests |
| VK_KHR_synchronization2 | Device Extension | Required for all tests |
| VK_KHR_swapchain | Device Extension | Required when WSI test type is used |
| VK_EXT_debug_utils | Instance Extension | Required when debug_utils test type is used |
| sparseBinding + sparseResidencyImage2D | Device Features | Required when bind_sparse test type is used |
| VK_INTEL_performance_query | Device Extension | Required when performance_configuration test type is used |
| VK_NV_low_latency2 | Device Extension | Required when out_of_band test type is used |
| WSI platform support | Platform | Required when WSI test type is used |

## Verification Methods

1. **Draw operations (small/large/small2/large2)**: Each thread renders a gradient and reads back the result. Verification checks that pixel values match the expected gradient pattern within a tolerance of 1 byte per channel.

2. **Sparse bind operations**: Alternates between buffer and image sparse bind. Verifies that the output buffer contains the expected fill value (0x12345678 for buffers) or sequential byte values (i%255 for images).

3. **WSI operations**: Acquires swapchain images, renders, and presents. No explicit pixel verification; success is measured by the operation completing without errors.

4. **Debug utils operations**: Wraps draw commands with `queueBeginDebugUtilsLabelEXT` / `queueEndDebugUtilsLabelEXT`. Verifies the draw result using the same gradient check.

5. **Performance configuration**: Acquires and releases INTEL performance configurations, resets query pools, and submits command buffers. Success is measured by operations completing without errors.

6. **Out-of-band operations**: Calls `queueNotifyOutOfBandNV` with `VK_OUT_OF_BAND_QUEUE_TYPE_RENDER_NV` before draw. Verifies the draw result.

7. **Device wait idle**: Submits buffer copy commands and calls `deviceWaitIdle`. Success is measured by the operation completing without errors.

8. **Thread failure detection**: Each `CaseThread` sets an `m_failed` flag if verification fails. After all threads join, the test instance checks for failures.

## Test Principles

1. **Concurrent queue access**: The core principle is that multiple threads can submit work to the same Vulkan queue without any external synchronization, relying on the `VK_DEVICE_QUEUE_CREATE_INTERNALLY_SYNCHRONIZED_BIT_KHR` flag to provide internal synchronization.

2. **Diverse operation types**: By combining different operation types across threads (draw, sparse bind, WSI, debug utils, performance queries, etc.), the tests exercise various Vulkan submission paths concurrently.

3. **Queue creation variants**: Tests different ways to create internally synchronized queues: single queue, first queue family synced, last queue family synced, and two queues from the same family with different sync flags.

4. **Custom device creation**: Each test creates a custom device with the required extensions and queue creation flags, since the default context device does not have internally synchronized queues.

5. **Fallback to single queue**: If the implementation does not support enough queue families or queues for the requested configuration, the test falls back to a single-queue configuration.

## Notes/Uncertainties

- **sync2-only**: The `internally_synchronized_queues` group is only added to the `synchronization2` test tree. The factory function `createInternallySynchronizedTests` takes a `SynchronizationType` parameter but it is only called with `SYNCHRONIZATION2`.
- **Non-SC only**: The test is excluded from Vulkan SC builds (`#ifndef CTS_USES_VULKANSC`).
- **WSI Android limitation**: When both thread 3 and thread 4 use WSI on Android (`TYPE_ANDROID`), the test is skipped because multiple concurrent WSI windows are not supported on Android.
- **Thread count**: Always exactly 4 threads per test, with threads 1 and 2 fixed to small/large image sync, and threads 3 and 4 varying.
- **Queue retrieval**: Uses `vk.getDeviceQueue2()` with `VK_DEVICE_QUEUE_CREATE_INTERNALLY_SYNCHRONIZED_BIT_KHR` to retrieve the internally synchronized queue handle.
- **Extensions enabled on custom device**: The custom device always enables `VK_KHR_internally_synchronized_queues` and `VK_KHR_synchronization2`, plus conditional extensions based on test types.
