# Understanding brief: internally synchronized queues

## One-sentence purpose

These tests verify that multiple threads can submit different kinds of work concurrently to the same Vulkan queue when it was created with `VK_DEVICE_QUEUE_CREATE_INTERNALLY_SYNCHRONIZED_BIT_KHR`.

## Registration and scope

This is a **Vulkan synchronization2-only, non-SC** family:

- `synchronization2.internally_synchronized_queues`
- 183 registered cases in the default [`synchronization2` mustpass](../../../mustpass/main/vk-default/synchronization2.txt)
- Not registered under `synchronization` (legacy). The legacy tree has a different `internally_synchronized_objects` family.

The factory accepts `SynchronizationType`, but the only call site adds it while constructing the synchronization2 group; the implementation always enables synchronization2 and uses `queueSubmit2` for the `small2` and `large2` operations.

## What each case does

1. Select two variable operation types from `small2`, `large2`, `bind_sparse`, `wsi`, `debug_utils`, `performance_configuration`, `out_of_band`, and `device_wait_idle`.
2. Create a custom device with `VK_KHR_internally_synchronized_queues` and `VK_KHR_synchronization2`, and create the requested queue configuration.
3. Retrieve an internally synchronized queue with `vkGetDeviceQueue2`.
4. Start four threads on that queue. Threads 1 and 2 always run legacy-submit small/large image draws; threads 3 and 4 run the selected operation types.
5. Join all threads and report failure if an operation or its result check fails.

Draw cases render a gradient and compare readback pixels. Sparse cases check copied buffer/image data. WSI, performance-query, and device-idle cases primarily require their operations to complete successfully; debug-utils and out-of-band cases also verify the draw result.

## Generated test names

The generator uses the Cartesian product of the eight variable operation types. Non-WSI cases are named `<type3>_<type4>` (for example, `small2_large2`). If WSI is selected, the name is `<wsi>_<type3>_<type4>` (for example, `headless_wsi_small2` or `xcb_bind_sparse_wsi`). WSI variants are generated for the supported WSI types; Android's double-WSI combination is omitted because concurrent WSI windows are unsupported there.

The default mustpass contains 49 non-WSI and 134 WSI cases (183 total). This count describes registered names, not guaranteed execution: `checkSupport()` skips cases when the required device/instance extensions, features, queue families, or platform support are absent.

## Important parameters

- Queue creation: single queue, first/last internally synchronized queue, or two internally synchronized queues selected by the generated parameters.
- Queue family relationship: same or different queue families.
- Required for every case: `VK_KHR_internally_synchronized_queues`, `VK_KHR_synchronization2`, and the corresponding `internallySynchronizedQueues` / `synchronization2` features.
- Conditional requirements: swapchain and WSI surface extension for WSI; `VK_EXT_debug_utils` for debug labels; sparse binding and sparse residency image 2D for sparse tests; `VK_INTEL_performance_query` and `VK_NV_low_latency2` for their respective cases.
- If the requested queue-family/queue-count arrangement is unavailable, the implementation falls back to a single queue where possible; if no suitable graphics queue exists, the case is not supported.

## Source and related documentation

- [Rewritten test page](vktSynchronizationInternallySynchronizedTests.md)
- [Source: vktSynchronizationInternallySynchronizedTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationInternallySynchronizedTests.cpp)
- [Registration: vktSynchronizationTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp)
- [Synchronization2 category](../../categories/synchronization2.md)
