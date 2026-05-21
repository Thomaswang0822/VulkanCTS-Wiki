# vktWsiSwapchainTests

## Overview

This file implements tests for `VkSwapchainKHR` creation, destruction, rendering, modification, image retrieval, acquisition, and private data. It covers swapchain parameter validation across all `TestDimension` values, OOM simulation, multi-swapchain rendering, device-group rendering, swapchain resizing, and the `VK_EXT_private_data` extension interaction with swapchains.

## Role

Implementation file — contains test case implementations and the `createSwapchainTests` registration function.

## Source

[vktWsiSwapchainTests.cpp](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2953-L2973)

## Registration Hierarchy

```text
wsi.headless.swapchain
├── create
├── simulate_oom
├── render
├── modify
├── destroy
├── get_images
├── acquire
└── private_data
```

> **Per-Platform Note:** The Level-3 root path uses "headless" as the representative platform. The same structure is replicated for all WSI platform types (e.g., `wsi.xcb.swapchain`, `wsi.wayland.swapchain`, etc.).

## Test Families

- **create** — Tests swapchain creation with various parameter dimensions. Each `TestDimension` value generates a test case that varies one swapchain creation parameter while keeping others at default. Additionally includes `image_swapchain_create_info` and `image_swapchain_create_info_concurrent` cases that test `VkImageSwapchainCreateInfoKHR` with exclusive and concurrent sharing modes respectively. Populated by [populateSwapchainGroup](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1523-L1541) using the `createSwapchainTest` function.

- **simulate_oom** — Simulates out-of-memory conditions during swapchain creation using allocation callbacks. Covers the same `TestDimension` values as `create` (including `image_extent`), but omits the two `image_swapchain_create_info` variants. Populated by the same [populateSwapchainGroup](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1523-L1541) using the `createSwapchainSimulateOOMTest` function.

- **render** — Rendering tests that create a swapchain and render frames. Contains 8 test cases: `basic` and `basic2` use `vkAcquireNextImageKHR` and `vkAcquireNextImage2KHR` respectively; `device_group` and `device_group2` test device-group swapchain rendering; `2swapchains`/`2swapchains2` and `10swapchains`/`10swapchains2` test rendering with multiple simultaneous swapchains. Populated by [populateRenderGroup](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2880-L2908).

- **modify** — Tests swapchain modification. Currently contains only `resize`, which destroys and recreates the swapchain with a new extent. The `resize` test is conditionally registered only when `PlatformProperties::swapchainExtent != SWAPCHAIN_EXTENT_MUST_MATCH_WINDOW_SIZE`. A source comment notes planned tests for modifying `preTransform`, `compositeAlpha`, and `presentMode`. Populated by [populateModifyGroup](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2918-L2929).

- **destroy** — Tests swapchain destruction scenarios: `null_handle` verifies destroying `VK_NULL_HANDLE` is a no-op; `old_swapchain` verifies destroying an old swapchain after creating a new one; `old_swapchain_acquired_image` verifies destroying an old swapchain after acquiring an image from it; `retired_swapchain_present` verifies presenting an image acquired before the swapchain was retired. Populated by [populateDestroyGroup](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2931-L2941).

- **get_images** — Tests `vkGetSwapchainImagesKHR`: `incomplete` verifies that `VK_INCOMPLETE` is returned when the image count parameter is too small; `count` verifies that the correct number of images is reported. Populated by [populateGetImagesGroup](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2910-L2916).

- **acquire** — Tests `vkAcquireNextImageKHR` error conditions: `too_many` verifies that acquiring more images than available returns `VK_NOT_READY` with zero timeout; `too_many_timeout` verifies the same with a non-zero timeout. Populated by [populateAcquireGroup](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2943-L2949).

- **private_data** — Tests `VK_EXT_private_data` interaction with swapchains. Covers all `TestDimension` values except `image_extent` (which is explicitly skipped), verifying that private data can be set and retrieved on the swapchain handle. Populated by [populateSwapchainPrivateDataGroup](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1024-L1035) using the `createSwapchainPrivateDataTest` function.

## Parameter Dimensions

| Dimension | Values / Range | Description |
|-----------|----------------|-------------|
| TestDimension | `min_image_count`, `image_format`, `image_extent`, `image_array_layers`, `image_usage`, `image_sharing_mode`, `pre_transform`, `composite_alpha`, `present_mode`, `clipped`, `exclusive_nonzero_queues` | Enum controlling which swapchain creation parameter is varied. Used in `create`, `simulate_oom`, and `private_data` families. See [TestDimension](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L340-L355). |
| WSI platform type | xlib, xcb, wayland, android, win32, metal, headless, direct_drm, direct | Passed as `vk::wsi::Type` to each test function; determines surface and platform behavior. |
| Swapchain count | 1, 2, 10 | Number of simultaneous swapchains in render tests. 2 and 10 are used in the `Nswapchains` variants. |
| Acquire method | `vkAcquireNextImageKHR`, `vkAcquireNextImage2KHR` | Distinguishes `basic` vs `basic2` and `Nswapchains` vs `Nswapchains2` render variants. |
| Sharing mode (image_swapchain_create_info) | exclusive, concurrent | `image_swapchain_create_info` uses exclusive; `image_swapchain_create_info_concurrent` uses concurrent. |

### TestDimension value generation details

- **min_image_count**: Iterates from `capabilities.minImageCount` up to `clamp(16, minImageCount, maxImageCount)` — see [generateSwapchainParameterCases](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L421-L434).
- **image_format**: Iterates over all `VkSurfaceFormatKHR` entries returned by `vkGetPhysicalDeviceSurfaceFormatsKHR` — see [L436-L446](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L436-L446).
- **image_extent**: Varies by platform property; includes fixed test sizes `{1,1}, {16,32}, {32,16}, {632,231}, {117,998}` clamped to capabilities, plus `currentExtent`, `minImageExtent`, and `maxImageExtent` — see [L448-L483](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L448-L483).
- **image_array_layers**: Iterates from 1 up to `min(capabilities.maxImageArrayLayers, 16)` — see [L485-L496](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L485-L496).
- **image_usage**: Enumerates all subsets of `capabilities.supportedUsageFlags` that are valid for the format — see [L498-L523](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L498-L523).
- **image_sharing_mode**: Tests `VK_SHARING_MODE_CONCURRENT` (exclusive is the base parameter default) — see [L525-L537](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L525-L537).
- **pre_transform**: Iterates over all bits set in `capabilities.supportedTransforms` — see [L539-L551](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L539-L551).
- **composite_alpha**: Iterates over all bits set in `capabilities.supportedCompositeAlpha` — see [L553-L565](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L553-L565).
- **present_mode**: Iterates over all present modes returned by `vkGetPhysicalDeviceSurfacePresentModesKHR` — see [L567-L577](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L567-L577).
- **clipped**: Tests both `VK_FALSE` and `VK_TRUE` — see [L579-L588](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L579-L588).
- **exclusive_nonzero_queues**: Tests `VK_SHARING_MODE_EXCLUSIVE` with `queueFamilyIndexCount = 2` — see [L590-L597](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L590-L597).

## Support / Feature Requirements

- **Device extension:** `VK_KHR_swapchain` — required for all tests.
- **Instance extension:** `VK_KHR_surface` — required for all tests.
- **Device extension:** `VK_EXT_private_data` — required for `private_data` tests; checked at runtime via `context.getPrivateDataFeatures().privateData`.
- **Instance extension:** `VK_KHR_device_group_creation` + **Device extension:** `VK_KHR_device_group` — required for `render.device_group` and `render.device_group2` tests.
- **Device extension:** `VK_KHR_bind_memory2` + `VK_KHR_swapchain` revision >= 69 — required for `create.image_swapchain_create_info` and `create.image_swapchain_create_info_concurrent` tests.
- **Device extension:** `VK_EXT_attachment_feedback_loop_layout` — optionally enabled when supported, to expand `image_usage` test coverage.
- **Queue family:** At least 2 distinct queue families supporting the surface — required for `image_sharing_mode` concurrent tests and `image_swapchain_create_info_concurrent`.
- **Platform property:** `swapchainExtent != SWAPCHAIN_EXTENT_MUST_MATCH_WINDOW_SIZE` — required for `modify.resize` to be registered.

## Verification Methods

- **API call success:** Create tests verify that `vkCreateSwapchainKHR` returns `VK_SUCCESS` for each generated parameter case. Format support is pre-checked via `vkGetPhysicalDeviceImageFormatProperties`; `VK_ERROR_FORMAT_NOT_SUPPORTED` causes the sub-case to be skipped — see [createSwapchainTest](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L619-L739).
- **OOM tolerance:** For `image_extent` at `maxImageExtent` and `min_image_count` above the minimum, `createSwapchainTest` catches `OutOfMemoryError` as a non-failure condition — see [L682-L714](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L682-L714).
- **Data round-trip:** Private data tests set a value via `vkSetPrivateDataEXT` and verify the same value is returned by `vkGetPrivateDataEXT` across 100 private data slots and 3 iterations — see [createSwapchainPrivateDataTest](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L747-L889).
- **OOM simulation:** `simulate_oom` tests inject allocation failures via callbacks and verify no memory leaks occur during swapchain creation — see [createSwapchainSimulateOOMTest](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L891).
- **Rendering loop success:** Render tests execute 600 frames of rendering via `WsiTriangleRenderer` and verify all Vulkan API calls succeed without errors.
- **VK_INCOMPLETE check:** `get_images.incomplete` verifies that `vkGetSwapchainImagesKHR` returns `VK_INCOMPLETE` when the output array is too small.
- **Result code check:** `acquire` tests verify that `vkAcquireNextImageKHR` returns `VK_NOT_READY` or times out as expected. `destroy.retired_swapchain_present` verifies the result of presenting from a retired swapchain.
- **No-op verification:** `destroy.null_handle` confirms that destroying a null swapchain handle does not crash or produce errors.

## Notes / Uncertainties

- The `create` and `simulate_oom` sub-groups share the same `populateSwapchainGroup` function but with different test function pointers (`createSwapchainTest` vs `createSwapchainSimulateOOMTest`). Both groups include the `image_swapchain_create_info` and `image_swapchain_create_info_concurrent` cases added at the end of `populateSwapchainGroup`.
- The `private_data` sub-group uses `populateSwapchainPrivateDataGroup` which explicitly skips `TEST_DIMENSION_IMAGE_EXTENT` (line 1029), resulting in 10 test cases instead of 11.
- The `modify.resize` test is conditionally registered based on `PlatformProperties::swapchainExtent` — it will not appear on platforms where the swapchain extent must match the window size. A source comment at [L2928](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2928) notes planned but unimplemented tests for modifying `preTransform`, `compositeAlpha`, and `presentMode`.
- Render test names use the convention of no suffix for `vkAcquireNextImageKHR` and `2` suffix for `vkAcquireNextImage2KHR`.
- The `createSwapchainSimulateOOMTest` function limits itself to at most 300 parameter cases and 1024 allocations — see [L893-L894](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L893-L894).
