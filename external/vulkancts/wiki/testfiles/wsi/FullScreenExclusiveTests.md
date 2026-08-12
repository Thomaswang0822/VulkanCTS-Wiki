## Overview

**Core question:** Does each full-screen-exclusive policy produce an allowed swapchain lifecycle and a consistent result when the test renders and presents frames?

- This page covers `vktWsiFullScreenExclusiveTests.cpp`, which implements the `full_screen_exclusive` test family registered under every platform-specific WSI branch.
- Each platform branch contains four test case leaves. The leaves select one `VkFullScreenExclusiveEXT` policy: `default`, `allowed`, `disallowed`, or `application_controlled`.
- The test creates a full-screen-sized native window, queries surface support with the selected policy, creates a swapchain, and presents 60 frames with `WsiTriangleRenderer`.
- The first three policies let the implementation manage exclusive mode. The application-controlled policy also calls `vkAcquireFullScreenExclusiveModeEXT` and `vkReleaseFullScreenExclusiveModeEXT`.
- The test checks WSI and exclusive-mode results. It does not compare rendered pixels.

## Background Knowledge

For the shared concepts surface constraints, swapchain ownership, and presentation, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- `VkSurfaceFullScreenExclusiveInfoEXT::fullScreenExclusive` is a swapchain policy. `DEFAULT` lets the implementation choose, `ALLOWED` permits exclusive mechanisms, `DISALLOWED` asks the implementation to avoid them, and `APPLICATION_CONTROLLED` assigns mode management to the application. These policies can affect capabilities, so the test includes the same structure in its surface query and swapchain creation.
- `VkSurfaceCapabilitiesFullScreenExclusiveEXT::fullScreenExclusiveSupported` reports whether the queried surface can use exclusive full-screen access. The Vulkan specification says that applications must not create an application-controlled swapchain when this value is `VK_FALSE`.
- Application-controlled access uses explicit ownership transitions. `vkAcquireFullScreenExclusiveModeEXT` returns `VK_SUCCESS` when the swapchain acquires exclusive access, while `VK_ERROR_INITIALIZATION_FAILED` means that access could not be acquired. A swapchain command can return `VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT` when platform changes remove the mode.

## Registration Hierarchy

The implementation registers the same four test case leaves under each platform-specific WSI branch. `headless` is the representative hierarchy used by the canonical validator:

```text
wsi.headless.full_screen_exclusive
├── default
├── allowed
├── disallowed
└── application_controlled
```

The default WSI mustpass list contains the same four leaves under `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, and `xlib`. The dispatcher invokes `createFullScreenExclusiveTests` from the per-platform `full_screen_exclusive` group. The separate `display`, `display_control`, and `acquire_drm_display` groups do not use this implementation.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| WSI platform | `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, `xlib` in the default mustpass list | Selects the platform surface extension and native display/window path. The full-screen policy and frame loop remain in the same implementation. | [WSI dispatcher](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L83), [default WSI mustpass paths](../../../mustpass/main/vk-default/wsi.txt#L30-L33) |
| Full-screen policy test case leaf | `default`, `allowed`, `disallowed`, `application_controlled` | Supplies the `fseType` value in `VkSurfaceFullScreenExclusiveInfoEXT` and selects whether the test performs explicit acquire/release. This is the primary behavioral axis. | [full-screen test registration](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L620-L637) |
| Fixed execution values | 60 frames, two requested swapchain images, FIFO present mode | Bounds the common rendering path. These values are not additional registered dimensions. | [swapchain setup and frame loop](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L392-L460) |

## Behavior Parameters

The full-screen policy test case leaf is the primary behavioral axis because it changes the policy passed through the surface and swapchain `pNext` chains and determines whether the test explicitly manages exclusive access.

### `default`: implementation-selected policy

The test sets `fullScreenExclusive` to `VK_FULL_SCREEN_EXCLUSIVE_DEFAULT_EXT`. The implementation chooses the full-screen transition behavior. The test then exercises the common swapchain creation and 60-frame presentation path without calling the explicit acquire or release commands.

### `allowed`: exclusive mode permitted

The test sets `fullScreenExclusive` to `VK_FULL_SCREEN_EXCLUSIVE_ALLOWED_EXT`. The implementation may use exclusive mechanisms when available. The test does not require the application to acquire or release the mode itself, so the result reflects the common swapchain and presentation path under this policy.

### `disallowed`: exclusive mode discouraged

The test sets `fullScreenExclusive` to `VK_FULL_SCREEN_EXCLUSIVE_DISALLOWED_EXT`. The implementation should avoid exclusive mechanisms that require disruptive transitions. The test uses the same swapchain and presentation flow as the other implementation-selected policies.

### `application_controlled`: explicit acquire and release

The test sets `fullScreenExclusive` to `VK_FULL_SCREEN_EXCLUSIVE_APPLICATION_CONTROLLED_EXT`. Before each frame, while the mode has not been acquired, it calls `vkAcquireFullScreenExclusiveModeEXT`. A successful call records ownership for the rest of the loop. After the device becomes idle, the test calls `vkReleaseFullScreenExclusiveModeEXT` if acquisition succeeded.

A failed acquire with `VK_ERROR_INITIALIZATION_FAILED` leaves the mode unacquired and allows the loop to continue. A lost-mode result from explicit acquire is logged but does not set `fullScreenLost`; results from image acquisition, presentation, or release are logged and recorded.

## Shader Analysis

The test uses `WsiTriangleRenderer::getPrograms()` to build the renderer's common shaders, but shader output is not the tested property and no pixel data enters the pass/fail decision. A shader walkthrough and SPIR-V subsection would therefore add detail without explaining full-screen-exclusive behavior. The relevant source only delegates program creation at [getBasicRenderPrograms](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L613-L616).

## Runtime Execution and Result Checking

- The test first requires `VK_EXT_full_screen_exclusive` in the device extension list. It creates the platform-specific instance and window, using `getFullScreenSize` with a `256 x 256` fallback, then creates a surface and a queue-capable device. `VK_KHR_surface` and `VK_KHR_swapchain` are required; `VK_KHR_get_surface_capabilities2` is enabled when advertised, and display or direct-DRM platform extensions are selected by the WSI type.
- The test makes the window visible. On Win32 it also calls `setForeground()` and records the returned `isForeground` value. For a Win32 case, it chains `VkSurfaceFullScreenExclusiveWin32InfoEXT` with the monitor handle into the surface query and swapchain creation structures.
- The test chains `VkSurfaceFullScreenExclusiveInfoEXT` with the selected `fseType` into `VkPhysicalDeviceSurfaceInfo2KHR` and queries `VkSurfaceCapabilitiesFullScreenExclusiveEXT`. A surface reporting `fullScreenExclusiveSupported == false` is not supported for this test.
- The swapchain requests a desired image count of two, which the helper clamps to the surface's minimum and maximum image-count limits, along with one color-attachment layer, exclusive sharing, opaque alpha, FIFO presentation, and the platform-appropriate extent. The same full-screen policy chain is attached to `VkSwapchainCreateInfoKHR`.
- `VK_ERROR_INITIALIZATION_FAILED` from swapchain creation is converted to a quality warning only for `application_controlled`, because the specification permits exclusive access to be unavailable for that requested combination. Other creation errors fail through the CTS result check.
- After swapchain creation, the test creates the triangle renderer, a resettable command pool, primary command buffers, and rings of fences and semaphores. The fence ring limits queued work while the loop reuses synchronization objects.
- For each of 60 frames, the application-controlled path retries acquisition while `fullScreenAcquired` is false. `VK_SUCCESS` records acquisition. `VK_ERROR_INITIALIZATION_FAILED` leaves it unacquired. `VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT` from explicit acquire is logged, but does not set `fullScreenLost`; the same result from image acquisition or presentation is recorded as mode loss. Other results are checked as Vulkan errors.
- The test waits for the reusable fence after the queue reaches its `maxQueuedFrames` limit, resets that fence, and calls `vkAcquireNextImageKHR`. A `VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT` result marks `fullScreenLost`; `VK_CHECK_WSI` handles the WSI result. If an image was acquired, the renderer records a frame, the queue submits it, and `vkQueuePresentKHR` presents it. A mode-loss result from presentation also marks `fullScreenLost`.
- If image acquisition returns mode loss, the test submits no command buffer and advances the synchronization ring. The device is idle before resources are released or the test returns.
- For `application_controlled`, the test releases exclusive mode after the loop when acquisition succeeded. A mode-loss result from release is logged and contributes to `fullScreenLost`.
- The source returns `pass("Rendering tests succeeded")` when `fullScreenAcquired` is true and `fullScreenLost` is false. Otherwise it returns a quality warning, distinguishing mode loss from failure to acquire. The final conditional also treats `!isForeground` for an application-controlled case as a pass condition, as shown in the source. See the risk note in `Failure Meaning`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `default` | WSI instance/device setup, surface capability query, swapchain creation, image acquisition, rendering submission, presentation, or a full-screen mode loss reported during the common path. |
| `allowed` | WSI instance/device setup, surface capability query, swapchain creation, image acquisition, rendering submission, presentation, or a full-screen mode loss reported during the common path. |
| `disallowed` | WSI instance/device setup, surface capability query, swapchain creation, image acquisition, rendering submission, presentation, or a full-screen mode loss reported during the common path. |
| `application_controlled` | The same common WSI failures, inability to create or acquire an application-controlled swapchain, failure or loss during explicit acquire/release, or the source's foreground-state result branch. |

### Cause Analysis

#### Common WSI or swapchain failure

**Possible failure symptoms:** The case throws `NotSupportedError`, fails because no surface format exists, or reports an unexpected result while creating the surface, device, swapchain, acquiring an image, submitting work, or presenting it.

**Possible implementation causes:** The selected platform path may not expose the required surface or swapchain support, may reject the policy-specific `pNext` chain, or may return an error during image ownership, queue submission, or presentation. The failing call and platform identify the next source-level investigation point.

#### Exclusive mode unavailable or not acquired

**Possible failure symptoms:** `application_controlled` cannot create its swapchain or finishes without acquiring the mode, and the test returns a quality warning rather than a hard failure for the expected unavailable-mode cases.

**Possible implementation causes:** The surface may report no exclusive capability, or the implementation may return `VK_ERROR_INITIALIZATION_FAILED` because the display cannot provide exclusive access for the requested surface and policy. The specification permits this result for acquisition and allows the application to retry acquisition.

#### Exclusive mode lost during a swapchain operation

**Possible failure symptoms:** `vkAcquireFullScreenExclusiveModeEXT`, `vkAcquireNextImageKHR`, `vkQueuePresentKHR`, or `vkReleaseFullScreenExclusiveModeEXT` returns `VK_ERROR_FULL_SCREEN_EXCLUSIVE_MODE_LOST_EXT`. The test logs the call site; it marks `fullScreenLost` for image acquisition, presentation, and release, but only logs the result for explicit acquire. The final status therefore treats explicit-acquire mode loss differently if a later acquire succeeds.

**Possible implementation causes:** A platform-specific display or window transition can remove exclusive access. The specification states that mode loss can end exclusivity, so the log's operation identifies whether the loss occurred while acquiring an image, presenting, or releasing the swapchain.

#### Foreground-state result branch

**Possible failure symptoms:** On Win32, `setForeground()` returns false. The source records this state in `isForeground` and includes `!isForeground` for an application-controlled test in the final pass condition.

**Possible implementation causes:** The source treats that predicate as sufficient for the pass branch when the application-controlled policy is active, even though the foreground state does not demonstrate successful exclusive acquisition. This is a source-level behavior to review rather than a claim about a driver or hardware defect.

## Case Pruning

### Requirement-based pruning

- The test requires the `VK_EXT_full_screen_exclusive` device extension, `VK_KHR_surface` for instance setup, and `VK_KHR_swapchain` for device setup. Missing required extensions produce `NotSupportedError`.
- The selected surface must report `fullScreenExclusiveSupported == true` through `VkSurfaceCapabilitiesFullScreenExclusiveEXT`. Unsupported surfaces are skipped as not supported.
- The selected platform must provide the WSI extension and a native display/window path. Display WSI adds `VK_KHR_display`; `direct_drm` adds `VK_EXT_direct_mode_display`; Win32 adds the monitor-specific structure when the test uses a Win32 surface.
- The test returns a hard failure when no `VkSurfaceFormatKHR` is available. It does not prune individual policy leaves based on rendered image contents because it never compares pixels.

### Design-based pruning

- The dispatcher runs the four policy leaves for every platform-specific WSI type. It does not add separate registered cases for window size, surface format, swapchain image count, present mode, or frame count.
- The test fixes the requested swapchain image count at two and uses FIFO presentation. These choices keep the synchronization and presentation path bounded while the policy remains the behavioral variable.
- The renderer's shader variants are not separate cases. The common triangle renderer supplies visual work, but full-screen-exclusive state and Vulkan return codes provide the observed result.

## Key Takeaways

- The four leaves differ in the `VkFullScreenExclusiveEXT` policy passed to both the capability query and swapchain creation. Only `application_controlled` calls the explicit acquire and release commands.
- The common loop presents 60 frames and records mode loss from image acquisition and presentation. The test checks lifecycle and API results, not rendered color values.
- A surface that cannot provide exclusive access is a supported reason to skip the case. Application-controlled swapchain creation and acquisition can also report quality warnings when exclusive access is unavailable.
- The source's final condition counts `!isForeground` as a pass for an application-controlled case. Preserve that behavior in the documentation until the implementation is reviewed. It is a risk when interpreting foreground-related results.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| WSI family dispatch | [createTypeSpecificTests](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L73) | Registers `full_screen_exclusive` under each platform-specific WSI branch. |
| Test parameter and extension setup | [TestParams and createDeviceWithWsi](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L63-L140) | Defines the platform and policy inputs and enables the device extensions used by the test. |
| Native window and swapchain configuration | [NativeObjectsFS and getBasicSwapchainParameters](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L213-L264) | Chooses the full-screen-sized window and baseline swapchain parameters. |
| Capability query and swapchain creation | [fullScreenExclusiveTest setup](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L304-L430) | Chains the policy, queries exclusive support, and creates the swapchain. |
| Acquire and presentation loop | [fullScreenExclusiveTest frame loop](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L452-L568) | Handles explicit acquisition, 60 frames, synchronization, image acquisition, submission, and presentation. |
| Release and final status | [fullScreenExclusiveTest result handling](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L576-L610) | Releases application-controlled mode and maps the observed state to pass or quality warning. |
| Policy registration | [createFullScreenExclusiveTests](../../../modules/vulkan/wsi/vktWsiFullScreenExclusiveTests.cpp#L620-L637) | Maps the four exact leaf names to their `VkFullScreenExclusiveEXT` values. |
| Full-screen policy semantics | [Vulkan WSI specification](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L3121-L3166) | Defines the policy structure and the four enum values. |
| Surface capability semantics | [VkSurfaceCapabilitiesFullScreenExclusiveEXT](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L3568-L3592) | Defines the support query and the application-controlled restriction. |
| Explicit mode transitions | [Full Screen Exclusive Control](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L4448-L4528) | Defines acquire, release, initialization failure, and mode-loss behavior. |
| Representative registration | [headless mustpass paths](../../../mustpass/main/vk-default/wsi.txt#L11538-L11541) | Confirms all four leaves under `wsi.headless.full_screen_exclusive`. |
