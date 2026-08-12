## Overview

The `wsi` test category collects tests that check how Vulkan connects surfaces, swapchains, presentation engines, and direct displays to native window systems.

Most test families repeat below each supported WSI platform. Three direct-display families sit directly under `wsi` because they do not use a platform-specific surface type.

## Background Knowledge

- A `VkSurfaceKHR` connects a Vulkan instance to a native window or display target. Surface queries report the formats, present modes, transforms, and limits that constrain swapchain creation.
- A swapchain contains presentable images owned in turn by the application and the presentation engine. The application acquires an image, submits work that makes it ready, and presents it back to the engine. Retirement and explicit release change which images remain available without destroying work that is already allowed to finish.
- Presentation is asynchronous. Present IDs, fences, waits, and timing records expose different completion or scheduling points without making presentation a synchronous queue operation.
- Direct-display WSI uses `VkDisplayKHR`, display modes, and display planes instead of an ordinary desktop window. DRM-specific commands connect those Vulkan objects to Linux connector ownership.

## Category Structure

```text
wsi
├── xlib
├── xcb
├── wayland
├── android
├── win32
├── metal
├── headless
├── direct_drm
├── direct
├── display
├── display_control
└── acquire_drm_display
```

The first nine branches repeat the same platform-routed test families. The last three are direct children of `wsi`. The registration-only dispatcher is folded into this page rather than represented by a separate rewritten Level-3 page.

## How the Families Fit Together

- **Native target and image lifecycle:** `surface` establishes the target's properties, while `swapchain` covers image creation, acquisition, retirement, and destruction.
- **Presentation behavior:** incremental regions, shared images, color spaces, full-screen ownership, maintenance operations, IDs, waits, and timing extensions vary how swapchain images reach the presentation engine.
- **Direct display control:** `display`, `display_control`, and `acquire_drm_display` cover display objects, intended power or event control, counters, and DRM ownership without a platform-specific window branch. The Level-3 pages distinguish executable checks from source paths that current validity or ownership gates prevent from producing a conformance result.

Together these families cover the WSI contract from native-target discovery through image presentation and direct-display ownership.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|--------------------------------|--------------|--------------------|
| `surface` | [Surface Tests](../testfiles/wsi/SurfaceTests.md) | Surface creation, lifecycle, capability queries, enumeration contracts, and native-window changes. |
| `swapchain` | [Swapchain Tests](../testfiles/wsi/SwapchainTests.md) | Swapchain creation dimensions, acquisition, rendering workloads, replacement, destruction, and private data. |
| `incremental_present` | [Incremental Present Tests](../testfiles/wsi/IncrementalPresentTests.md) | Damage-region metadata and per-image partial-update history. |
| `shared_presentable_image` | [Shared Presentable Image Tests](../testfiles/wsi/SharedPresentableImageTests.md) | One-image swapchains under demand and continuous refresh. |
| `colorspace`, `colorspace_compare` | [Color Space Tests](../testfiles/wsi/ColorSpaceTests.md) | Advertised color spaces, HDR metadata, rendering, and the intended raw-pixel comparison, including its current source-validity limitation. |
| `display_timing` | [Display Timing Tests](../testfiles/wsi/DisplayTimingTests.md) | Desired presentation times and past-presentation records from `VK_GOOGLE_display_timing`. |
| `present_id_wait` | [Present ID and Wait Tests](../testfiles/wsi/PresentIdWaitTests.md) | Version 1 and version 2 present IDs, waits, ordering, and timeouts. |
| `present_timing` | [Present Timing Tests](../testfiles/wsi/PresentTimingTests.md) | Stage timestamps, timing-result queues, time domains, and target times from `VK_EXT_present_timing`. |
| `maintenance1` | [Maintenance1 Tests](../testfiles/wsi/Maintenance1Tests.md) | Present-fence resource-lifetime signals, compatible modes, scaling, permitted deferred allocation, and explicit image release. |
| `full_screen_exclusive` | [Full-Screen Exclusive Tests](../testfiles/wsi/FullScreenExclusiveTests.md) | Full-screen-exclusive policies and application-controlled acquire/release behavior. |
| `display` | [Display Tests](../testfiles/wsi/DisplayTests.md) | Display, plane, mode, surface, capability, and extensible enumeration APIs, with validity limits for two source paths. |
| `display_control` | [Display Control Tests](../testfiles/wsi/DisplayControlTests.md) | Reachable device-event registration and the currently gated counter, display-power, and display-event paths. |
| `acquire_drm_display` | [Acquire DRM Display Tests](../testfiles/wsi/AcquireDrmDisplayTests.md) | DRM connector lookup, display acquisition, ownership errors, and release. |

## Category Notes

- [`createWsiTests()`](../../modules/vulkan/wsi/vktWsiTests.cpp#L76-L91) creates the category root, the nine platform branches, and the three direct-display branches.
- Platform availability and build configuration prune branches before execution. A missing branch does not by itself indicate a conformance failure.
