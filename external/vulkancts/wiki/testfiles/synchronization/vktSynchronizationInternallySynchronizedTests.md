# vktSynchronizationInternallySynchronizedTests

## Overview

Tests for the `VK_KHR_internally_synchronized_queues` extension, which allows multiple threads to submit work to the same Vulkan queue concurrently without external synchronization. These tests create queues with the `VK_DEVICE_QUEUE_CREATE_INTERNALLY_SYNCHRONIZED_BIT_KHR` flag, spawn multiple threads that each perform different operations on the same queue simultaneously, and verify that all operations complete correctly without data corruption.

This is a **sync2-only** test file (non-SC). It is registered under the `synchronization2` category only. Although the factory function takes a `SynchronizationType` parameter, it is only ever called with `SYNCHRONIZATION2`.

## Role of File

Provides the `internally_synchronized_queues` test group, which validates that internally synchronized queues correctly handle concurrent submissions from multiple threads. Each test spawns 4 threads, each performing a different operation type on the same queue, and verifies that all threads produce correct results without interference.

## Source Code

- [vktSynchronizationInternallySynchronizedTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp)

## Registration Path

```
synchronization2.internally_synchronized_queues
```

Registered in the sync2 path via `createInternallySynchronizedTests(testCtx, type)` added to the `synchronization2` group in [vktSynchronizationTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp) (line 130).

## Test Hierarchy

```
internally_synchronized_queues
+-- <testType3>_<testType4>           (core combination)
+-- <wsiType>_<testType3>_<testType4> (WSI variants, when WSI is involved)
```

### Test Type Names

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

| Family | Class | Description |
|--------|-------|-------------|
| InternallySynchronizedQueuesTestCase | InternallySynchronizedQueuesTestCase | Creates a custom device with internally synchronized queues, spawns 4 concurrent threads each running a different operation on the same queue, and verifies all threads complete successfully. |

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
