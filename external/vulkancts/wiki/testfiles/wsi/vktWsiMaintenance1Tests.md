# vktWsiMaintenance1Tests

## Overview

This file implements tests for the VK_KHR_surface_maintenance1, VK_KHR_swapchain_maintenance1, VK_EXT_surface_maintenance1, and VK_EXT_swapchain_maintenance1 extensions. These extensions provide mechanisms for present fences, dynamic present mode switching, swapchain scaling and gravity, deferred memory allocation, and releasing acquired swapchain images. The EXT and KHR versions of these extensions are functionally identical; the tests alternate between preferring one or the other and automatically fall back to whichever is available.

## Role of file

Implementation file. Contains all test logic, configuration structs, helper utilities, and test group population functions for the maintenance1 WSI extension tests.

## Source code

[vktWsiMaintenance1Tests.cpp](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp)

## Registration Hierarchy

```text
wsi.headless.maintenance1
├── present_fence
├── present_modes
├── scaling
├── deferred_alloc
└── release_images
```

## Test Families

### present_fence

Registered at [vktWsiMaintenance1Tests.cpp#L2664](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2664). Populated by `populatePresentFenceGroup` ([vktWsiMaintenance1Tests.cpp#L1156](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1156)).

Tests the present fence mechanism introduced by VK_KHR_swapchain_maintenance1. Present fences allow applications to receive a signal when a present operation has completed, enabling proper resource lifecycle management. The group is organized by present mode, and each present mode sub-group contains:

- **basic**: Performs multiple present iterations with a fence associated with each present. Verifies that fences signal correctly after presentation.
- **ordering**: Verifies the ordering guarantee of present fence signals -- that fences are signaled in the same order as the corresponding present operations.
- **multi_swapchain**: (Not available on Android, direct DRM, or direct display platforms) Tests present fences with multiple swapchains presenting simultaneously.
- **mult_swapchain_ordering**: (Not available on all platforms) Verifies fence signal ordering across multiple swapchains.
- **null_handles**: (Not available on all platforms) Tests present fences where some fence handles are VK_NULL_HANDLE (randomly omitted), verifying the implementation handles sparse fence arrays correctly.

### present_modes

Registered at [vktWsiMaintenance1Tests.cpp#L2666](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2666). Populated by `populatePresentModesGroup` ([vktWsiMaintenance1Tests.cpp#L1393](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1393)).

Tests the present mode compatibility query and dynamic present mode switching. The group is organized by present mode, and each present mode sub-group contains:

- **query**: Queries compatible present modes via `VkSurfacePresentModeCompatibilityEXT` chained to `vkGetPhysicalDeviceSurfaceCapabilities2KHR`. Validates that returned modes are supported, include the query mode, have no duplicates, and are consistent across re-queries with different buffer sizes (zero, too small, correct, and oversized).
- **change_modes**: Creates a swapchain with a list of compatible present modes and randomly switches between them during presentation using `VkSwapchainPresentModeInfoEXT`.
- **change_modes_multi_swapchain**: (Not available on all platforms) Switches between compatible present modes across multiple swapchains simultaneously.
- **change_modes_with_deferred_alloc**: (Not available on all platforms) Switches between compatible modes while the swapchain uses deferred memory allocation.

Additionally, a **heterogenous** sub-group (not available on all platforms) tests switching present modes across multiple swapchains where each swapchain may use a different present mode.

### scaling

Registered at [vktWsiMaintenance1Tests.cpp#L2668](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2668). Populated by `populateScalingGroup` ([vktWsiMaintenance1Tests.cpp#L2089](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2089)), which delegates to `populateScalingTests` ([vktWsiMaintenance1Tests.cpp#L1927](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1927)).

Tests the scaling and gravity capabilities introduced by VK_EXT_surface_maintenance1. The group is organized by present mode, and each present mode sub-group contains:

- **query**: A sub-group with two tests:
  - **basic**: Queries `VkSurfacePresentScalingCapabilitiesEXT` and validates that only valid scaling and gravity flag bits are reported.
  - **verify_compatible_present_modes**: Verifies that all compatible present modes report identical scaling and gravity capabilities.
- **one_to_one**, **aspect_stretch**, **stretch**: Sub-groups per scaling flag. Each contains gravity combinations (min/max/center for X and Y axes, except stretch which does not use gravity). Each gravity combination includes tests for various swapchain-to-window size and aspect ratio relationships:
  - **same_size_and_aspect**: No actual scaling needed.
  - **swapchain_bigger_same_aspect**: Swapchain is 2x the window size.
  - **swapchain_smaller_same_aspect**: Swapchain is half the window size.
  - **swapchain_taller**: Swapchain has the same width but is 1.5x taller.
  - **swapchain_bigger_taller_aspect**: Swapchain is bigger and taller.
  - **swapchain_smaller_taller_aspect**: Swapchain is smaller but taller.
  - **swapchain_wider**: Swapchain has the same height but is 1.5x wider.
  - **swapchain_bigger_wider_aspect**: Swapchain is bigger and wider.
  - **swapchain_smaller_wider_aspect**: Swapchain is smaller but wider.

A **resize_window** sub-group repeats all of the above but resizes the window after swapchain creation rather than creating the swapchain at a different size.

### deferred_alloc

Registered at [vktWsiMaintenance1Tests.cpp#L2670](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2670). Populated by `populateDeferredAllocGroup` ([vktWsiMaintenance1Tests.cpp#L2099](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2099)).

Tests the deferred memory allocation feature enabled by `VK_SWAPCHAIN_CREATE_DEFERRED_MEMORY_ALLOCATION_BIT_EXT`. The group is organized by present mode, and each present mode sub-group contains:

- **basic**: Creates a swapchain with deferred memory allocation and performs present iterations, verifying that images are properly allocated on first acquire.
- **bind_image**: (Not available for shared demand/continuous refresh present modes) Uses `VkBindImageMemorySwapchainInfoKHR` to bind swapchain images manually after deferred allocation.
- **bind_image_multi_swapchain**: (Not available on all platforms) Tests deferred allocation with bind image memory across multiple swapchains.

### release_images

Registered at [vktWsiMaintenance1Tests.cpp#L2672](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2672). Populated by `populateReleaseImagesGroup` ([vktWsiMaintenance1Tests.cpp#L2575](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2575)).

Tests the `vkReleaseSwapchainImagesKHR` function for releasing acquired swapchain images back to the swapchain without presenting them. The group is organized by present mode, then by scaling flag (no_scaling, stretch), and each combination includes:

- **basic**: Acquires multiple images and releases the non-presented ones after presentation.
- **release_before_present**: Releases acquired images before the present operation completes.
- **resize_window**: Resizes the window before acquire, then releases images.
- **resize_window_after_acquire**: Resizes the window after acquire, then releases images.
- **resize_window_after_acquire_release_before_retire**: Resizes the window after acquire, releases images before retiring the swapchain (when VK_ERROR_OUT_OF_DATE_KHR is returned).

## Parameter Dimensions

### Present Modes

All test families iterate over the following present modes (subject to runtime support checks):

| Mode | Name in tree |
|------|-------------|
| VK_PRESENT_MODE_IMMEDIATE_KHR | immediate |
| VK_PRESENT_MODE_MAILBOX_KHR | mailbox |
| VK_PRESENT_MODE_FIFO_KHR | fifo |
| VK_PRESENT_MODE_FIFO_RELAXED_KHR | fifo_relaxed |
| VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR | demand |
| VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR | continuous |
| VK_PRESENT_MODE_FIFO_LATEST_READY_KHR | fifo_latest_ready |

### Scaling Flags (scaling and release_images families)

| Flag | Name in tree |
|------|-------------|
| VK_PRESENT_SCALING_ONE_TO_ONE_BIT_EXT | one_to_one |
| VK_PRESENT_SCALING_ASPECT_RATIO_STRETCH_BIT_EXT | aspect_stretch |
| VK_PRESENT_SCALING_STRETCH_BIT_EXT | stretch |
| 0 (no scaling) | no_scaling (release_images only) |

### Gravity Flags (scaling family only)

| Flag | Name in tree |
|------|-------------|
| VK_PRESENT_GRAVITY_MIN_BIT_EXT | min |
| VK_PRESENT_GRAVITY_MAX_BIT_EXT | max |
| VK_PRESENT_GRAVITY_CENTERED_BIT_EXT | center |

### EXT vs KHR Preference

Tests alternate between preferring the EXT and KHR versions of the extensions. If only one version is supported, the test automatically falls back to the available version regardless of preference. This is tracked via the `preferExt` boolean in test config structs.

### Present Fence Variants (present_fence family)

- Single swapchain with basic fence signaling
- Single swapchain with fence ordering verification
- Multiple swapchains (3 or 5) with fence signaling
- Null fence handles (randomly omitted VK_NULL_HANDLE entries)

## Support/Feature Requirements

### Required Extensions

- **VK_KHR_surface**: Base WSI surface support.
- **VK_KHR_swapchain**: Base swapchain support.
- **VK_KHR_get_surface_capabilities2**: Required for querying surface capabilities with present mode chaining.
- **VK_KHR_surface_maintenance1** or **VK_EXT_surface_maintenance1**: Instance extension providing present mode compatibility and scaling capability queries. At least one must be supported.
- **VK_KHR_swapchain_maintenance1** or **VK_EXT_swapchain_maintenance1**: Device extension providing present fences, present mode switching, deferred allocation, and image release. At least one must be supported for tests that require swapchain maintenance features (present_fence, deferred_alloc, release_images, and the change_modes tests within present_modes).

### Conditionally Required Extensions

- **VK_KHR_get_physical_device_properties2**: Required if not already a core extension for the API version in use.
- **VK_KHR_device_group_creation**: Required when bind image memory is used (deferred_alloc bind_image tests).
- **VK_KHR_device_group**: Required when bind image memory is used.
- **VK_KHR_bind_memory2**: Required when bind image memory is used and Vulkan 1.1 is not supported.
- **VK_EXT_present_mode_fifo_latest_ready**: Required for the `fifo_latest_ready` present mode tests.
- **VK_KHR_shared_presentable_image**: Required for shared demand/continuous refresh present mode tests.
- **VK_KHR_display**: Required for display surface types.

### Feature Requirements

- `VkPhysicalDeviceSwapchainMaintenance1FeaturesEXT::swapchainMaintenance1` must be VK_TRUE when swapchain maintenance1 device extension is enabled.
- `VkPhysicalDevicePresentModeFifoLatestReadyFeaturesEXT::presentModeFifoLatestReady` must be VK_TRUE when VK_EXT_present_mode_fifo_latest_ready is enabled.

## Verification Methods

- **Present fence signal verification**: Tests wait on present fences after presentation and verify they signal correctly. The ordering variant checks that fences are signaled in the same order as their corresponding present operations by scanning fences from newest to oldest and ensuring no unsignaled fence appears after a signaled one ([vktWsiMaintenance1Tests.cpp#L770-L793](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L770-L793)).
- **Compatible present mode query validation**: Queries `VkSurfacePresentModeCompatibilityEXT` and verifies: all returned modes are supported by the surface, the queried mode is included, there are no duplicates, and results are consistent across re-queries with varying buffer sizes ([vktWsiMaintenance1Tests.cpp#L1231-L1267](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1231-L1267)).
- **Scaling capability query validation**: Queries `VkSurfacePresentScalingCapabilitiesEXT` and verifies only valid flag bits are reported. Also verifies that all compatible present modes report identical scaling capabilities ([vktWsiMaintenance1Tests.cpp#L1546-L1647](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1546-L1647)).
- **Present mode switching**: Creates swapchains with a list of compatible present modes and randomly switches modes during presentation using `VkSwapchainPresentModeInfoEXT`, verifying no errors occur.
- **Deferred allocation lifecycle**: Creates swapchains with `VK_SWAPCHAIN_CREATE_DEFERRED_MEMORY_ALLOCATION_BIT_EXT` and verifies images can be acquired and presented correctly, including with manual image memory binding.
- **Image release workflow**: Exercises `vkReleaseSwapchainImagesKHR` in various scenarios (before present, after present, after window resize, before swapchain retirement), verifying the operation succeeds and subsequent acquire/present cycles work correctly.

## Notes/Uncertainties

- The EXT and KHR versions of the surface_maintenance1 and swapchain_maintenance1 extensions are functionally identical. Tests alternate preference between them to cover both without duplicating all test cases. If only one version is available, the test automatically uses it regardless of preference.
- Multi-swapchain present tests are disabled on Android (known implementation bug unrelated to maintenance1), VK_KHR_display (direct), and direct DRM platforms due to WSI wrapper limitations.
- The `bind_image` test under `deferred_alloc` is excluded for shared present modes (VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR and VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR) due to unrelated driver crashes.
- The scaling tests render colored quadrants to swapchain images and present them, but do not currently capture and verify the visual output of scaling. A TODO comment in the source ([vktWsiMaintenance1Tests.cpp#L1909](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1909)) notes this limitation.
- The iteration count for present loop tests varies based on present mode: FIFO modes use 120 iterations (approximately 2 seconds at 60Hz), while non-vsync modes use 250 iterations. Window resize tests reduce iterations: FIFO modes with frequent resizes use 60 iterations (2x reduction), while non-FIFO modes use 5 iterations (50x reduction).
- The `release_images` tests randomly decide how many images to acquire and whether to present in each iteration, providing varied coverage of the release workflow.
