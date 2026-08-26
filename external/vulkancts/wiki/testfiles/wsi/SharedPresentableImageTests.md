## Overview

**Core question:** Can Vulkan keep one shared swapchain image renderable and presentable under both shared refresh policies?

- This page covers the `shared_presentable_image` test family. `vktWsiSharedPresentableImageTests.cpp` implements it, and the WSI dispatcher registers it below each applicable platform.
- Every test case creates a one-image swapchain, acquires image index `0` once, transitions it to `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR`, and renders 300 frames without moving it out of that layout.
- The `demand` and `continuous` test case leaves differ in presentation cadence. Demand refresh presents each rendered frame, while continuous refresh presents only the first frame.
- The CTS checks Vulkan results, the acquired index, shared-present usage support, swapchain status, and bounded out-of-date recovery. It does not read back pixels or check presentation timing.

## Background Knowledge

For the shared concepts swapchain image ownership and asynchronous presentation, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- A **shared presentable image** is the single image acquired from a swapchain that uses `VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR` or `VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR`. The application and presentation engine may access it concurrently after its first presentation.
- `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR` is valid only for shared presentable images and supports any use allowed for that image. The application can leave the image in this layout while rendering and presenting instead of alternating between an attachment layout and `VK_IMAGE_LAYOUT_PRESENT_SRC_KHR`.
- Demand refresh requires a presentation request to guarantee that the presentation engine updates from the image. Continuous refresh requires one initial request, then the presentation engine refreshes from the shared image without further requests.

## Registration Hierarchy

The source registers the same test family below nine WSI platform branches. Current mustpass data has scaled cases for `android` and `metal`; the other branches contain `scale_none`.

```text
wsi.android.shared_presentable_image
├── scale_none
├── scale_up
└── scale_down

wsi.direct.shared_presentable_image
└── scale_none

wsi.direct_drm.shared_presentable_image
└── scale_none

wsi.headless.shared_presentable_image
└── scale_none

wsi.metal.shared_presentable_image
├── scale_none
├── scale_up
└── scale_down

wsi.wayland.shared_presentable_image
└── scale_none

wsi.win32.shared_presentable_image
└── scale_none

wsi.xcb.shared_presentable_image
└── scale_none

wsi.xlib.shared_presentable_image
└── scale_none
```

Each scaling intermediate node contains transform and composite-alpha intermediate nodes. The executable leaves are `demand` and `continuous`. For example, `dEQP-VK.wsi.headless.shared_presentable_image.scale_none.identity.opaque.demand` is one complete registered path.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| WSI platform | `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, `xlib` in current mustpass data | Runs the same shared-image logic through each platform-specific surface integration. | [WSI family registration](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L83); mustpass ranges for [Android](../../../mustpass/main/vk-default/wsi.txt#L4129-L4344), [direct display](../../../mustpass/main/vk-default/wsi.txt#L7817-L7888), [direct DRM](../../../mustpass/main/vk-default/wsi.txt#L11359-L11430), [headless](../../../mustpass/main/vk-default/wsi.txt#L15295-L15366), [Metal](../../../mustpass/main/vk-default/wsi.txt#L19936-L20151), [Wayland](../../../mustpass/main/vk-default/wsi.txt#L24003-L24074), [Win32](../../../mustpass/main/vk-default/wsi.txt#L27924-L27995), [XCB](../../../mustpass/main/vk-default/wsi.txt#L31846-L31917), and [Xlib](../../../mustpass/main/vk-default/wsi.txt#L35768-L35839) |
| Scaling | `scale_none`, `scale_up`, `scale_down` | Chooses an image extent equal to, smaller than, or larger than the current surface extent. The source registers the scaled intermediate nodes only for WSI types whose platform properties allow scaled swapchain extents. | [extent selection](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L489-L512), [conditional registration](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L1001-L1042) |
| Surface transform | `identity`, `rotate_90`, `rotate_180`, `rotate_270`, `horizontal_mirror`, `horizontal_mirror_rotate_90`, `horizontal_mirror_rotate_180`, `horizontal_mirror_rotate_270`, `inherit` | Sets `preTransform`; unsupported values produce a not-supported result. | [support check](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L514-L531), [registered values](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L979-L991) |
| Composite alpha | `opaque`, `pre_multiplied`, `post_multiplied`, `inherit` | Sets how surface composition interprets the image alpha channel; unsupported values produce a not-supported result. | [swapchain fields](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L533-L556), [registered values](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L992-L999) |
| Present mode leaf | `demand`, `continuous` | Controls when the test calls `vkQueuePresentKHR`; this is the primary behavioral axis. | [present-mode registration](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L971-L978) |
| Surface format | Every reported format and color-space pair whose image format supports the selected usage | Creates a separate swapchain configuration so the shared-present flow runs across usable surface formats. | [format loop](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L533-L574) |

## Behavior Parameters

The present mode test case leaf is the primary behavioral axis because it changes the contract between rendering and presentation requests.

### `demand`: present every rendered frame

`demand` selects `VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR`. The test signals a render semaphore and calls `vkQueuePresentKHR` after every draw, which guarantees that the presentation engine receives a request to use the updated shared image. The presentation engine may also read the image at other times under the extension rules.

### `continuous`: present once, then keep rendering

`continuous` selects `VK_PRESENT_MODE_SHARED_CONTINUOUS_REFRESH_KHR`. The test signals a render semaphore and calls `vkQueuePresentKHR` for frame zero, then submits later draws without more presentation requests. This exercises the continuous-refresh contract in which the presentation engine continues to refresh from the shared image after the initial request.

## Shader Analysis

The test generates a vertex shader that draws 16 quads from `gl_VertexIndex` and a fragment shader that derives a changing color from the quad index, fragment coordinates, and a `frameNdx` push constant. These shaders provide repeated color-attachment writes to the shared image, but the CTS does not check their arithmetic or pixel output. Shader code does not control the pass condition, so this page does not include a representative shader walkthrough.

## Runtime Execution and Result Checking

- The test creates a WSI-specific instance, surface, queue, and device with `VK_KHR_swapchain` and `VK_KHR_shared_presentable_image`. It queries surface formats, present modes, ordinary surface capabilities, and `VkSharedPresentSurfaceCapabilitiesKHR`.
- It requires `sharedPresentSupportedUsageFlags` to include `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT`. Swapchain image usage is the intersection of ordinary and shared-present usage flags.
- For each usable surface format, it creates a swapchain with `minImageCount = 1`, the selected extent, transform, alpha mode, and shared present mode. It then creates the render pass, graphics pipeline, image view, and framebuffer for that image.
- The test acquires the image once with `vkAcquireNextImageKHR` and checks that the returned index is `0`. One command buffer transitions it from `VK_IMAGE_LAYOUT_UNDEFINED` to `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR`.
- The render pass uses `VK_ATTACHMENT_LOAD_OP_LOAD`, `VK_ATTACHMENT_STORE_OP_STORE`, and `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR` as both the initial and final attachment layout. The presentation engine may access the image while the application continues to render, so the test does not discard its contents or transition it away from the shared layout.
- Each swapchain configuration runs 300 frames. The test rotates through six fences, six render semaphores, and six command-buffer slots. Before reusing a slot, it waits for and resets the fence, then frees the completed command buffer.
- Each frame pushes `frameNdx`, records one draw, and submits it. `demand` signals a semaphore and presents every frame. `continuous` does so only on frame zero. The test calls `vkGetSwapchainStatusKHR` after every frame.
- A `VK_ERROR_OUT_OF_DATE_KHR` triggers swapchain-configuration regeneration and resource recreation. The test restarts the current configuration at frame zero and permits up to 20 such recoveries. The result collector records other Vulkan errors, or another out-of-date result after that limit, as failures.
- After all frames and format configurations finish, the CTS returns the collected result. There is no image readback, screenshot comparison, tearing check, or timing assertion.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `demand` | Per-frame demand-refresh presentation, render-to-present synchronization, shared-image layout use, swapchain status, or common shared-swapchain lifecycle failure. |
| `continuous` | Initial continuous-refresh presentation, continued rendering without later presentation requests, shared-image layout use, swapchain status, or common shared-swapchain lifecycle failure. |

### Cause Analysis

#### Demand-refresh request or synchronization failure

**Possible failure symptoms:** A `demand` case reports an error during a render submission, semaphore-backed presentation, per-swapchain present result, or status query before completing 300 frames for a configuration.

**Possible implementation causes:** The implementation may mishandle repeated `vkQueuePresentKHR` calls for the same acquired image, the wait semaphore that makes color-attachment writes available to presentation, or demand-refresh presentation state. The Vulkan WSI rules require an application to present when it needs a guaranteed demand-refresh update.

#### Continuous-refresh startup or continued-rendering failure

**Possible failure symptoms:** A `continuous` case succeeds on the initial presentation but later reports an error while rendering to the same image without further presentation requests, or it fails during the initial semaphore-backed presentation.

**Possible implementation causes:** The implementation may require presentation requests that the continuous-refresh contract does not require, or it may mishandle continued application writes while the presentation engine refreshes from the shared image. Source-level investigation is needed to distinguish presentation-engine state from queue, image, or synchronization handling when the reported Vulkan error does not identify the failing subsystem.

#### Common shared-swapchain lifecycle or capability failure

**Possible failure symptoms:** Either leaf can fail because shared color-attachment usage is missing, acquisition returns an index other than `0`, image creation or rendering rejects `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR`, a status call fails, resource recreation fails, or out-of-date recovery exceeds 20 attempts.

**Possible implementation causes:** The implementation may report capabilities inconsistent with later swapchain or image use, violate the one-image shared-swapchain contract, reject a supported operation in the required shared layout, or fail to maintain valid shared-swapchain state across rendering, status queries, and recreation. This flow prunes unsupported present modes, transforms, alpha modes, and image formats instead of classifying them as conformance failures.

## Case Pruning

### Requirement-based pruning

- Missing required instance or device extensions produce a not-supported result before the render loop.
- The selected shared present mode must appear in the surface's reported present modes. The selected transform and composite alpha flag must also appear in the surface capabilities.
- The shared-present usage flags must include `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT`. The format loop omits a reported surface format when `vkGetPhysicalDeviceImageFormatProperties` returns `VK_ERROR_FORMAT_NOT_SUPPORTED` for the selected usage.
- Platform, surface, queue, and native display or window support determine whether a WSI branch can execute on a system.

### Design-based pruning

- The source always registers `scale_none`. It registers `scale_up` and `scale_down` only when `wsiTypeSupportsScaling` reports `SWAPCHAIN_EXTENT_SCALED_TO_WINDOW_SIZE` for that WSI type.
- The matrix fixes the swapchain to one image and one array layer because shared present modes use a single shared presentable image.
- The test uses the available surface format list instead of registering format names as separate test case leaves.

## Key Takeaways

- The test acquires one image once and leaves it in `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR` through all rendering and presentation work for that swapchain.
- `demand` and `continuous` test different presentation-request rules while sharing the same resource lifecycle, render workload, and status checks.
- Passing means that all checked Vulkan operations and CTS invariants survive the fixed frame and configuration loops. It does not prove pixel accuracy, tear-free output, or presentation timing.
- See `## Failure Meaning` to interpret failures in each present-mode leaf.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| WSI dispatcher | [createTypeSpecificTests](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L73) | Places `shared_presentable_image` below each applicable WSI platform branch. |
| Test matrix | [createSharedPresentableImageTests](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L964-L1044) | Registers scaling, transform, composite-alpha, and present-mode values. |
| Swapchain configuration | [generateSwapchainConfigs](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L477-L575) | Selects extents, filters support, sets one image, and builds per-format configurations. |
| Shared usage query | [getPhysicalDeviceSurfaceCapabilities](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L577-L600) | Queries `VkSharedPresentSurfaceCapabilitiesKHR` and checks color-attachment usage. |
| Persistent shared layout | [createRenderPass](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L317-L354) | Keeps the attachment in `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR`. |
| Initial acquisition and transition | [initSwapchainResources](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L663-L735) | Acquires image zero once and performs the only layout transition. |
| Per-frame presentation policy | [render](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L754-L834) | Implements fencing, rendering, mode-dependent presentation, and status queries. |
| Recovery and completion | [iterate](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L836-L916) | Handles out-of-date recovery, frame count, format iteration, and final result collection. |
| Generated workload | [Programs::init](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L918-L960) | Defines the quad vertex shader and changing-color fragment shader. |
| Present-mode semantics | [Vulkan WSI chapter](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L4392-L4414) | Defines demand-refresh and continuous-refresh behavior. |
| Shared-image lifetime and access | [Vulkan shared presentable image rules](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L5652-L5689) | Defines one-image acquisition, concurrent access, and request cadence. |
| Shared-present layout | [Vulkan image layout rules](../../../../vulkan-docs/src/chapters/resources.adoc#L5423-L5429) | Defines valid use of `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR`. |
| Mustpass registration | Mustpass ranges for [Android](../../../mustpass/main/vk-default/wsi.txt#L4129-L4344), [direct display](../../../mustpass/main/vk-default/wsi.txt#L7817-L7888), [direct DRM](../../../mustpass/main/vk-default/wsi.txt#L11359-L11430), [headless](../../../mustpass/main/vk-default/wsi.txt#L15295-L15366), [Metal](../../../mustpass/main/vk-default/wsi.txt#L19936-L20151), [Wayland](../../../mustpass/main/vk-default/wsi.txt#L24003-L24074), [Win32](../../../mustpass/main/vk-default/wsi.txt#L27924-L27995), [XCB](../../../mustpass/main/vk-default/wsi.txt#L31846-L31917), and [Xlib](../../../mustpass/main/vk-default/wsi.txt#L35768-L35839) | Confirms concrete registered paths and platform-specific scaling coverage across all nine platform branches. |
