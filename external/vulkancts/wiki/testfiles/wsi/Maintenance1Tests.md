## Overview

**Core question:** Does the WSI implementation maintain correct ownership, completion, and capability behavior when an application changes how it presents swapchain images?

This page covers `vktWsiMaintenance1Tests.cpp`, which implements the `wsi.headless.maintenance1` test family and the corresponding per-platform groups. The source registers five test families:

- `present_fence` checks resource-lifetime completion and ordering signals attached to presentation.
- `present_modes` checks compatible-mode queries and mode changes during presentation.
- `scaling` checks surface scaling and gravity capabilities and exercises configured size differences.
- `deferred_alloc` checks swapchains that permit deferred image allocation and optional application-side image binding.
- `release_images` checks explicit release of acquired images, including resize and swapchain-retirement paths.

The tests use transfer commands to fill swapchain images. They do not use programmable shaders. The page explains the registered matrix, host and device sequence, validation rules, and what failures indicate.

## Background Knowledge

For the shared concepts swapchain image ownership, release, and asynchronous presentation, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- The `swapchainMaintenance1` device feature gates the swapchain-maintenance operations and flags used by these tests; the surface-maintenance query structures are enabled separately by a surface-maintenance extension. Deferred allocation lets an implementation postpone backing an image until `vkAcquireNextImageKHR` returns its index. A present fence signals after the relevant queue operations complete and the presentation engine has taken references to the associated payloads, which makes it a resource-lifetime signal; it need not wait for display of the image to complete. See [deferred allocation](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L6309-L6314) and [present fences](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L7351-L7392).
- A swapchain created with a compatible present-mode list can select one of those modes in a later `VkPresentInfoKHR` operation. Already queued images keep their previous mode, while the current and later images use the selected mode. See [dynamic present modes](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8436-L8464).

## Registration Hierarchy

```text
wsi.headless.maintenance1
├── present_fence
├── present_modes
├── scaling
├── deferred_alloc
└── release_images
```

`vktWsiTests.cpp` routes the same implementation through each WSI type. The old page and the source use `headless` as the representative path; platform-specific mustpass files contain the supported subset for each WSI type.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Test family | `present_fence`, `present_modes`, `scaling`, `deferred_alloc`, `release_images` | Selects the maintenance1 contract under test. | [`createMaintenance1Tests`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2661-L2673) |
| Present mode | `immediate`, `mailbox`, `fifo`, `fifo_relaxed`, `demand`, `continuous`, `fifo_latest_ready` | Selects the presentation scheduling behavior used for queries, presents, allocation, and release. Runtime support checks remove unavailable modes. | [`populatePresentFenceGroup`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1156-L1170) |
| Scaling mode | `one_to_one`, `aspect_stretch`, `stretch`; `no_scaling` for `release_images` | Selects the surface scaling contract. `no_scaling` keeps the release family independent of scaling support. | [`populateScalingTests`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1943-L1951), [`populateReleaseImagesGroup`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2591-L2598) |
| Gravity | `min`, `max`, `center` on each axis | Selects the placement of a nonmatching swapchain rectangle for the non-`stretch` scaling modes. | [`populateScalingTests`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1953-L1961) |
| Size and aspect | `same_size_and_aspect`, `swapchain_bigger_same_aspect`, `swapchain_smaller_same_aspect`, `swapchain_taller`, `swapchain_bigger_taller_aspect`, `swapchain_smaller_taller_aspect`, `swapchain_wider`, `swapchain_bigger_wider_aspect`, `swapchain_smaller_wider_aspect` | Changes whether the swapchain or window differs in size and aspect ratio. `resize_window` applies the mismatch by resizing after swapchain creation. | [`scalingTest`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1649-L1789), [`populateScalingTests`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2019-L2062) |
| Present-fence case | `basic`, `ordering`, `multi_swapchain`, `mult_swapchain_ordering`, `null_handles` | Selects basic signaling, signal ordering, multiple swapchains, or sparse fence arrays. | [`populatePresentFenceGroup`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1188-L1213) |
| Present-mode case | `query`, `change_modes`, `change_modes_multi_swapchain`, `change_modes_with_deferred_alloc`, and `heterogenous` leaves | Separates capability-query checks from mode changes on one or more swapchains. | [`populatePresentModesGroup`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1421-L1505) |
| Deferred allocation case | `basic`, `bind_image`, `bind_image_multi_swapchain` | Selects ordinary delayed allocation or explicit `VkBindImageMemorySwapchainInfoKHR` binding. | [`populateDeferredAllocGroup`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2121-L2151) |
| Release case | `basic`, `release_before_present`, `resize_window`, `resize_window_after_acquire`, `resize_window_after_acquire_release_before_retire` | Selects when the window changes and when the test releases acquired images relative to submission, present, and swapchain retirement. | [`populateReleaseImagesGroup`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2612-L2648) |
| Extension preference | `preferExt` true or false | Alternates preference for the EXT and KHR maintenance1 names. `chooseExt` falls back when only one version is available. | [`chooseExt`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L83-L111) |

The source uses `demand` and `continuous` for the two shared present modes. It omits `bind_image` for those modes and omits multi-swapchain cases for Android, direct DRM, and direct display WSI types.

## Behavior Parameters

The primary behavioral axis is the test family. Each family checks a different maintenance1 operation or contract.

### `present_fence` | resource-lifetime completion and fence ordering

The test attaches `VkSwapchainPresentFenceInfoEXT` to `VkPresentInfoKHR`, presents repeatedly, and waits for the corresponding fences. The `ordering` variants scan fences from the newest pending operation toward the oldest one. Once a later fence has signaled, an earlier fence must not remain unsignaled. Multi-swapchain variants repeat the check for three or five swapchains; `null_handles` leaves some fence entries as `VK_NULL_HANDLE`.

### `present_modes` | query and dynamic mode selection

The `query` case chains `VkSurfacePresentModeCompatibilityEXT` into `vkGetPhysicalDeviceSurfaceCapabilities2KHR`. It exercises count-only, undersized, exact-sized, and oversized output arrays. The change cases create a swapchain with the returned compatible list, then attach `VkSwapchainPresentModeInfoEXT` to later presents. The `heterogenous` family gives three swapchains different initial modes and changes them during presentation.

### `scaling` | scaling and gravity configuration

The query cases reject undefined scaling or gravity bits and compare capabilities across compatible modes. The execution cases attach `VkSwapchainPresentScalingCreateInfoEXT` to swapchain creation, choose the requested gravity on each axis, and present a swapchain whose size or aspect ratio differs from the window. The `resize_window` branch creates the swapchain first and changes the window instead. The source fills four quadrants with color, but it does not capture the display to verify the visual placement.

### `deferred_alloc` | allocation timing and image binding

The basic case creates the swapchain with `VK_SWAPCHAIN_CREATE_DEFERRED_MEMORY_ALLOCATION_BIT_EXT`, then acquires and presents images. In `bind_image`, the test creates a compatible `VkImage` for each swapchain image and binds it with `VkBindImageMemorySwapchainInfoKHR`. With deferred allocation, it performs that binding lazily when the image index first returns from acquire. Multi-swapchain cases apply the same process to two swapchains.

### `release_images` | explicit release of acquired images

Each iteration chooses how many images to acquire, whether to present one of them, whether to resize the window, and the order of the remaining indices. The test releases every acquired image except the presented image. It can release before present, after present, or while handling an out-of-date result and retiring the old swapchain. Shared present modes reacquire their single image after a release or swapchain recreation.

## Shader Analysis

These tests contain no shader source or generated shader artifact. They use transfer operations such as `vkCmdClearColorImage` and `vkCmdCopyBufferToImage`, so no `shader-analyzer` or `shader-disassembler` walkthrough applies.

## Runtime Execution and Result Checking

- `createInstanceWithWsi` enables `VK_KHR_surface`, the WSI platform extension, `VK_KHR_get_surface_capabilities2` when available, and the selected `VK_EXT_surface_maintenance1` or `VK_KHR_surface_maintenance1` extension; it may enable both maintenance extensions to keep the instance and device extension variants compatible. `createDeviceWithWsi` enables `VK_KHR_swapchain`, the selected swapchain maintenance extension when required, and `swapchainMaintenance1` in the feature chain. It also enables optional device-group, FIFO-latest-ready, and shared-present extensions when the device exposes them. See [instance and device setup](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L114-L262).
- Each case creates a native display and window, creates a surface, checks present-mode support, selects a surface format and transform, and creates the needed swapchain objects. Shared present modes use one image and skip repeated acquire operations after the first acquire.
- The present and deferred cases submit transfer commands that transition an acquired image, clear it, or copy four color buffers into it. They signal semaphores for presentation and wait on present fences before destroying dependent synchronization objects.
- `getIterations` uses 120 iterations for FIFO modes and 250 for non-FIFO modes. Resize-heavy cases use 60 iterations for FIFO modes and 5 for other modes. The scaling family uses 100 iterations.
- Release cases use a deterministic `de::Random` seed derived from the configuration. They vary acquire count, present choice, release order, and resize occurrence, then wait on a submission fence before releasing images that might still be in device use.
- An `VK_ERROR_OUT_OF_DATE_KHR` result triggers swapchain recreation. The release family tests whether the old swapchain's acquired images can be released before or after retirement, then checks that the new swapchain has the same image count.
- The test reports failure for invalid query contents, inconsistent capability values, a failed WSI result, an unsignaled or out-of-order fence, or an unexpected image-count change during recreation. The scaling family returns pass after successful execution, not after a pixel comparison.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `present_fence` | Incorrect present-fence signaling or ordering, invalid multi-swapchain/null-handle handling, or a failed present operation. |
| `present_modes` | Incorrect compatible-mode query results or an invalid dynamic present-mode transition. |
| `scaling` | Invalid capability bits, inconsistent capabilities across compatible modes, or a failed scaling configuration/present operation. |
| `deferred_alloc` | The implementation failed to make a deferred image usable by the time acquire returned its index, or failed a deferred bind/present sequence. |
| `release_images` | The implementation rejected a valid release sequence, mishandled released ownership during resize or retirement, or returned an unexpected WSI result. |

### Cause Analysis

#### Present completion and ordering

**Possible failure symptoms:** A present call returns an unexpected result, a present fence does not signal before the wait limit, or the ordering check finds an unsignaled fence after a later fence has signaled.

**Possible implementation causes:** The implementation may associate a fence with the wrong present operation, signal it before the relevant queue operations complete or before the presentation engine has taken the required payload references, or fail to preserve the ordering guarantee required for present fences. The source and Vulkan WSI chapter define the observable contract, but a failure does not by itself identify whether the cause lies in the host-side setup, driver, or presentation engine.

#### Compatible present mode query

**Possible failure symptoms:** The query returns an unsupported mode, omits the queried mode, returns duplicates, changes its result across equivalent buffer sizes, overwrites a sentinel past the returned count, or returns an unexpected `VkResult` for a zero or undersized array.

**Possible implementation causes:** The surface capability query may mishandle the `VkSurfacePresentModeCompatibilityEXT` count and array contract, or it may report a mode set that does not match the surface's supported modes. The test cannot localize the defect beyond that query behavior.

#### Scaling capability or configuration

**Possible failure symptoms:** The capability query reports undefined scaling or gravity bits, compatible modes report different capability sets, or swapchain creation or presentation fails for a supported scaling configuration.

**Possible implementation causes:** The surface may report flags outside the Vulkan-defined bitmasks, expose inconsistent data for compatible modes, or reject a configuration that its capability query advertised. The source does not capture the display, so this family cannot diagnose an incorrect visual placement that still produces successful API calls.

#### Deferred allocation and binding

**Possible failure symptoms:** The basic case fails to acquire or present an image, or a bind-image case fails while binding or using the image returned by acquire.

**Possible implementation causes:** The implementation may fail to make a deferred image fully backed before acquire returns its index, or mishandle the swapchain-image binding relationship. The test does not observe whether an implementation actually postpones allocation, because the deferred-allocation flag permits rather than requires that optimization.

#### Acquired-image release and retirement

**Possible failure symptoms:** `vkReleaseSwapchainImagesKHR` returns an unexpected result, a later acquire or present fails, or swapchain recreation changes the image count unexpectedly.

**Possible implementation causes:** The implementation may release an image while device work still uses it, fail to return a released image to the acquisition pool, or mishandle acquired images when an out-of-date result retires the old swapchain. The test waits on submission fences before release where required, so a failure after that wait points to the exercised WSI ownership or retirement behavior rather than to an unverified assumption about the bug location.

## Case Pruning

### Requirement-based pruning

- Every case requires the base WSI and swapchain extensions. Cases that use maintenance1 operations require one surface maintenance1 extension and, where applicable, one swapchain maintenance1 extension with `swapchainMaintenance1` enabled.
- Runtime checks skip unsupported present modes and scaling or gravity configurations.
- `fifo_latest_ready` requires `VK_EXT_present_mode_fifo_latest_ready` and its feature when the mode is selected. Shared modes require the corresponding shared-present support.
- Bind-image cases require device-group support and `VK_KHR_bind_memory2` when the API version does not provide the needed core functionality.
- Multi-swapchain cases require a WSI type that can create the required independent native windows and surfaces. The source excludes Android, direct DRM, and direct display.

### Design-based pruning

- The source omits `bind_image` for `demand` and `continuous` shared present modes.
- The release family tests `no_scaling` and `stretch`; it does not repeat the complete scaling flag matrix because release behavior is its primary contract.
- `stretch` does not use gravity. The generator still constructs the gravity loops, then places the test cases directly under the scaling flag group.
- Present-mode, extension-preference, and release choices alternate deterministic configuration bits to cover combinations without duplicating separate implementation functions.

## Key Takeaways

- The page groups five behavior contracts implemented by one source file. The test family, not the present mode, identifies the contract being checked.
- Present fences test resource-lifetime completion and ordering, while explicit image release tests ownership transitions that do not end in presentation.
- Compatible-mode and scaling queries are checked as data contracts before the source uses their results to create or present a swapchain.
- Deferred allocation changes when the implementation must back an image. Bind-image cases add an explicit binding path after acquire.
- Scaling cases exercise configuration and successful presentation only. They do not verify the displayed pixels.
- Platform support and runtime capability checks prune cases before execution, so a missing case in a platform-specific mustpass list does not imply a missing implementation family.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Extension selection and feature setup | [`chooseExt`, `createInstanceWithWsi`, and `createDeviceWithWsi`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L83-L262) | Establishes KHR/EXT fallback, required extensions, and feature enabling. |
| Present fence execution | [`presentFenceTest`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L795-L1154) | Builds the acquire, submit, present, fence, and cleanup sequence. |
| Present fence registration | [`populatePresentFenceGroup`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1156-L1221) | Defines present mode values and fence variants. |
| Compatible-mode query execution | [`presentModesQueryTest`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1231-L1391) | Checks counts, sentinels, supported modes, duplicates, and stable results. |
| Mode-change registration | [`populatePresentModesGroup`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1393-L1507) | Defines query, mode-change, multi-swapchain, deferred, and heterogeneous cases. |
| Scaling execution | [`scalingQueryTest`, `scalingQueryCompatibleModesTest`, and `scalingTest`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L1546-L1925) | Implements capability checks and colored-quadrant presentation. |
| Deferred allocation registration | [`populateDeferredAllocGroup`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2099-L2157) | Defines deferred and bind-image coverage. |
| Image release execution | [`releaseImagesTest`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2179-L2567) | Implements randomized acquire, release, resize, out-of-date, and retirement paths. |
| Family registration | [`createMaintenance1Tests`](../../../modules/vulkan/wsi/vktWsiMaintenance1Tests.cpp#L2661-L2673) | Defines the five direct children shown in the hierarchy. |
| Dispatcher routing | [`createTypeSpecificTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L74) | Routes `maintenance1` into each WSI type. |
| Mustpass evidence | [`wsi.txt`](../../../mustpass/main/vk-default/wsi.txt) | Contains platform-specific `dEQP-VK.wsi.<type>.maintenance1...` leaves, including the headless maintenance1 paths. |
| Swapchain ownership and release semantics | [Vulkan WSI chapter](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L5600-L5621) | Defines acquire, present, and explicit release ownership. |
| Deferred allocation semantics | [Vulkan WSI chapter](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L6309-L6314) | Defines when deferred swapchain image memory must become available. |
| Present mode and fence semantics | [Vulkan WSI chapter](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8436-L8585) | Defines mode selection and present-fence behavior. |
| Release command requirements | [Vulkan WSI chapter](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8605-L8649) | Defines `vkReleaseSwapchainImagesKHR` and its feature requirement. |
