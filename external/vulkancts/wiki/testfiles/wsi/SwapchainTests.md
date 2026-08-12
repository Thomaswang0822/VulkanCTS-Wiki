## Overview

**Core question:** Does the implementation preserve the swapchain contract through creation, use, replacement, destruction, image queries, acquisition pressure, and object metadata operations?

- This page covers the `swapchain` test family implemented and registered by [`vktWsiSwapchainTests.cpp`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L340-L2973).
- The source groups eight kinds of behavior under one file: parameterized creation, allocation-failure handling, rendering and presentation, resizing, destruction and retirement, image enumeration, bounded acquisition, and private data.
- The same hierarchy is instantiated for each WSI platform. This page uses `wsi.headless.swapchain` as the representative root while preserving the shared child names.
- Most checks concern host-visible API results and object lifetime. The rendering cases use a fixed triangle shader as a workload but do not compare pixels.

## Background Knowledge

For the shared concepts surface constraints and the swapchain acquire-present ownership cycle, see [Background Knowledge](../../categories/wsi.md#background-knowledge) of the `wsi` page.

- Passing a valid `oldSwapchain` to `vkCreateSwapchainKHR` retires the old swapchain. No more images may be acquired from it, but an image acquired before retirement may still be presented.

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

The WSI dispatcher registers this `swapchain` test family below each platform-specific branch. The direct children above are behavioral intermediate nodes implemented in the same source file.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| WSI platform | `xlib`, `xcb`, `wayland`, `android`, `win32`, `metal`, `headless`, `direct_drm`, `direct` | Selects native window, surface, and platform extent behavior. Availability depends on the build and mustpass configuration. | [WSI type names](../../../framework/vulkan/vkWsiUtil.cpp#L64-L70), [WSI dispatcher](../../../modules/vulkan/wsi/vktWsiTests.cpp#L76-L83) |
| Test family behavior | `create`, `simulate_oom`, `render`, `modify`, `destroy`, `get_images`, `acquire`, `private_data` | Chooses the swapchain contract being exercised. This is the primary behavioral axis. | [`createSwapchainTests`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2953-L2973) |
| Creation dimension | `min_image_count`, `image_format`, `image_extent`, `image_array_layers`, `image_usage`, `image_sharing_mode`, `pre_transform`, `composite_alpha`, `present_mode`, `clipped`, `exclusive_nonzero_queues` | Changes one `VkSwapchainCreateInfoKHR` field at a time from a valid baseline. `create` and `simulate_oom` register all eleven values; `private_data` omits `image_extent`. | [`populateSwapchainGroup`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1523-L1540), [`populateSwapchainPrivateDataGroup`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1024-L1033) |
| Image-alias creation | `image_swapchain_create_info`, `image_swapchain_create_info_concurrent` | Creates application-owned images associated with swapchain memory, using exclusive or concurrent queue-family sharing. | [`populateSwapchainGroup`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1523-L1541) |
| Render acquisition API | no suffix, suffix `2` | No suffix uses `vkAcquireNextImageKHR`; suffix `2` uses `vkAcquireNextImage2KHR`. | [`populateRenderGroup`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2880-L2907) |
| Render topology | `basic`, `device_group`, `device_group2`, `2swapchains`, `10swapchains`, plus suffixed variants | Selects one swapchain, a device-group path, or a presentation batch containing two or ten swapchains. | [`populateRenderGroup`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2880-L2907) |
| Resize extent | capability-clamped `128x128`, `256x256`, `512x512` | Replaces and renders swapchains at half, equal, and double the desired `256x256` size. Duplicate sizes can result after clamping. | [`getSwapchainSizeSequence`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2368-L2382) |
| Exhausted-image timeout | `0`, `50000000` ns | Selects the non-waiting `VK_NOT_READY` path or the finite-wait `VK_TIMEOUT` path for one extra acquisition request. | [acquisition-limit tests](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2768-L2868) |

The creation generator gives each dimension a source-specific value set:

- `min_image_count` ranges from `minImageCount` through a cap of 16, subject to `maxImageCount`.
- `image_format`, `pre_transform`, `composite_alpha`, and `present_mode` use values advertised for the surface.
- `image_extent` combines fixed sizes with current, minimum, and maximum extents when the platform model permits them.
- `image_array_layers` ranges from 1 through the smaller of `maxImageArrayLayers` and 16.
- `image_usage` enumerates supported, image-format-compatible nonzero flag subsets.
- `image_sharing_mode` adds the concurrent case. The baseline already uses exclusive sharing.
- `clipped` covers `VK_FALSE` and `VK_TRUE`.
- `exclusive_nonzero_queues` keeps exclusive sharing while setting `queueFamilyIndexCount` to 2, checking that an irrelevant nonzero count is not consumed in exclusive mode.

See [`generateSwapchainParameterCases`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L383-L605) for the exact generated records.

## Behavior Parameters

The direct test family child is the primary behavioral axis because each value changes the swapchain contract under test.

### `create`: capability-derived creation and swapchain-memory images

The parameter leaves create a swapchain for every generated record that passes the image-format property query. Maximum extents and image counts above the required minimum may exhaust memory, so those pressure cases accept an out-of-memory result rather than treating it as a conformance failure.

The two `image_swapchain_create_info` leaves take a different path. They create one application-owned `VkImage` per swapchain image, connect each image to the swapchain through `VkImageSwapchainCreateInfoKHR`, bind it with `VkBindImageMemorySwapchainInfoKHR`, and render through those aliases. The concurrent leaf supplies two queue-family indices.

### `simulate_oom`: allocation-failure cleanup

This path reuses the creation matrix while a deterministic allocator fails one allocation position at a time. For each generated record, the test advances the number of successful allocations until swapchain creation succeeds, then validates the callback record after the objects have been destroyed. It reports invalid callback behavior as a failure. Reaching the bounded allocation limit or observing no allocation callbacks yields a quality warning in the documented cases.

The shared population function also registers `image_swapchain_create_info` and `image_swapchain_create_info_concurrent` below `simulate_oom`. Those two leaves call the ordinary image-alias helper and do not inject allocation failures.

### `render`: acquire, submit, and present

`basic` and `basic2` run the same 600-frame loop with different acquisition entry points. Each frame waits for a reusable fence, acquires an image, records a triangle draw, submits work that waits on the image-ready semaphore, and presents after the rendering-complete semaphore is signaled.

The multi-swapchain leaves rotate across two or ten surfaces. Once one frame has been prepared for every swapchain, one `vkQueuePresentKHR` call carries all accumulated swapchains, indices, and semaphores. The test checks both the global result and every per-swapchain result.

`device_group` submits and presents through a logical device group in local presentation mode. `device_group2` creates split-instance image aliases, binds swapchain memory across two physical devices, renders vertical regions using both devices, and presents through the first device in remote presentation mode.

### `modify`: resize by replacement

`resize` creates three capability-clamped extents. Each new creation receives the previous handle through `oldSwapchain`, renders 60 frames, waits for device idle, and then becomes the old swapchain for the next size. The case checks replacement and continued rendering rather than modifying an existing swapchain in place.

### `destroy`: null and retired-swapchain lifetime

- `null_handle` calls `vkDestroySwapchainKHR` with `VK_NULL_HANDLE` using default and custom allocators. The custom allocator must record no allocation or free operation.
- `old_swapchain` replaces a swapchain and destroys the retired handle before cleaning up the replacement.
- `old_swapchain_acquired_image` acquires and waits for an old image before replacement, destroys the retired swapchain, then confirms that acquisition from the new swapchain still completes.
- `retired_swapchain_present` acquires an image, prepares it for presentation, retires the swapchain, and presents the already-acquired image. It accepts `VK_SUCCESS`, `VK_SUBOPTIMAL_KHR`, or `VK_ERROR_OUT_OF_DATE_KHR`.

### `get_images`: count and partial enumeration

`incomplete` allocates a vector containing all image handles but asks `vkGetSwapchainImagesKHR` to write only half of it. The command must return `VK_INCOMPLETE`, preserve the supplied output count, and leave entries beyond the returned range untouched.

`count` first queries the image count, then supplies an array with one extra element and a count one larger than required. The second call must overwrite the count with the original value.

### `acquire`: one request beyond the guaranteed limit

Both leaves query the actual swapchain image count `S` and the surface minimum `M`, then acquire `S - M + 1` images. The extra request uses another unsignaled fence. With timeout zero, the accepted results are `VK_SUCCESS`, `VK_SUBOPTIMAL_KHR`, and `VK_NOT_READY`. With a 50 ms timeout, they are `VK_SUCCESS`, `VK_SUBOPTIMAL_KHR`, and `VK_TIMEOUT`.

The success and suboptimal results remain legal because an image may become available during the call. The test rejects other results and waits only on fences associated with successful acquisitions.

### `private_data`: swapchain-handle metadata round trip

For every included creation dimension, this path creates 100 private-data slots. It checks the initial zero value on non-Android platforms, stores `i * i * i + 1` in each slot for the swapchain object, and reads each value back. It repeats the sequence three times, recreating all slots between iterations. Android omits the initial-zero assertion because the specification has a swapchain-specific erratum for that platform.

## Shader Analysis

The rendering-related cases load fixed shaders from `WsiTriangleRenderer::getPrograms`: a vertex shader rotates a triangle using the frame index, and a fragment shader writes magenta. Shader code is not part of the tested behavior. The tests do not inspect shader outputs or compare pixels, so a representative shader walkthrough would not clarify the swapchain contract. Shader compilation and drawing only provide real queue work before presentation.

## Runtime Execution and Result Checking

- Every path creates the platform's native objects, a `VkSurfaceKHR`, and a device whose queue family supports that surface. Creation paths query capabilities before building legal parameter records.
- Rendering paths query the actual swapchain images and allocate synchronization objects according to that count. Image-ready semaphores order acquisition before rendering; rendering-complete semaphores order rendering before presentation. Fences limit in-flight work and protect reused command buffers.
- The baseline and device-group render loops execute 600 frames. Multi-swapchain loops execute `180 * swapchainCount` frames. Each image-alias creation case and each resize extent executes 60 frames.
- Render validation is API-oriented. The code checks acquisition results, index bounds, submissions, presentation results, and the final idle wait. It does not read swapchain pixels back.
- Creation validation checks `vkGetPhysicalDeviceImageFormatProperties` before creating each swapchain. `VK_ERROR_FORMAT_NOT_SUPPORTED` skips that generated record; another unexpected query result fails the case.
- OOM simulation tests at most 300 generated records and 1024 first-failing-allocation positions per record. After object teardown, `validateAndLog` checks that allocation callback activity is valid and balanced.
- Private-data validation reads every stored value from every slot. Image enumeration validates result codes, counts, and untouched output entries. Lifetime cases rely on explicit result checks and successful follow-up operations.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `create` | Capability-derived swapchain parameters or swapchain-memory alias binding are rejected or mishandled. |
| `simulate_oom` | Swapchain creation does not unwind allocation failures cleanly, or allocation callbacks are used incorrectly. |
| `render` | Acquisition, synchronization, rendering submission, device-group routing, multi-swapchain presentation, or result reporting fails. |
| `modify` | Swapchain replacement across supported extents, `oldSwapchain` retirement, or rendering on the replacement fails. |
| `destroy` | Null-handle destruction, retired-swapchain lifetime, acquired-image lifetime, or presentation from a retired swapchain violates the tested contract. |
| `get_images` | Swapchain image enumeration returns the wrong count/result or writes beyond the reported output range. |
| `acquire` | Exhausted-image acquisition returns an unaccepted result or fails to complete according to the bounded timeout mode. |
| `private_data` | Private data associated with a swapchain starts with the wrong value where required or fails a set/get round trip. |

### Cause Analysis

#### Capability-derived creation or alias binding failure

**Possible failure symptoms:** A generated record that passed the prerequisite format query cannot create a swapchain outside the accepted memory-pressure cases, or application-created alias images cannot be bound and used for rendering.

**Possible implementation causes:** The implementation may apply surface limits, sharing-mode fields, image equivalence rules, or `VkBindImageMemorySwapchainInfoKHR` incorrectly. The exact failing dimension narrows the source-level investigation to the corresponding `VkSwapchainCreateInfoKHR` field or alias-binding path.

#### Allocation-failure cleanup or callback failure

**Possible failure symptoms:** Injected OOM escapes as an unexpected result, creation never reaches a successful allocation position within the bound, or callback validation finds an unmatched or invalid allocation record.

**Possible implementation causes:** A swapchain creation error path may retain host allocations, free them with incompatible callbacks, or perform callback operations that the recorder rejects. A callback-limit quality warning requires source-level investigation before attributing it to a leak.

#### Rendering, synchronization, or presentation failure

**Possible failure symptoms:** Acquisition returns an unexpected result, an image index is out of range, queue submission fails, a global or per-swapchain presentation result is rejected, or the device cannot become idle.

**Possible implementation causes:** The failing leaf distinguishes ordinary acquisition from `vkAcquireNextImage2KHR`, batched multi-swapchain presentation, and device-group routing. Potential causes include incorrect semaphore ordering, swapchain image state tracking, per-swapchain result reporting, or device-mask and peer-memory handling. The test does not compare pixels, so a failure does not by itself prove a fragment-output defect.

#### Swapchain replacement or lifetime failure

**Possible failure symptoms:** A replacement cannot render at a supported extent, destroying a null or retired handle has observable side effects, the new swapchain stops working after old-handle destruction, or presentation of a previously acquired retired-swapchain image returns an unaccepted result.

**Possible implementation causes:** The implementation may retire `oldSwapchain` incorrectly, release acquired-image resources too early, retain an invalid dependency between old and new handles, or mishandle the explicit right to present an image acquired before retirement.

#### Image enumeration failure

**Possible failure symptoms:** The partial query does not return `VK_INCOMPLETE`, reports the wrong count, overwrites entries beyond that count, or the full query changes the count unexpectedly.

**Possible implementation causes:** The implementation may not follow the two-call enumeration convention, may report inconsistent swapchain image inventory, or may write past the caller-provided array extent.

#### Bounded acquisition failure

**Possible failure symptoms:** The extra zero-timeout call returns neither a successful acquisition nor `VK_NOT_READY`, or the finite-timeout call returns neither a successful acquisition nor `VK_TIMEOUT`.

**Possible implementation causes:** The implementation may calculate the acquired-image limit incorrectly, wait despite a zero timeout, mishandle timeout expiration, or report an invalid result when no image is available. A successful acquisition is not a defect because presentation activity may release an image while the call runs.

#### Private-data association failure

**Possible failure symptoms:** A non-Android initial query is nonzero, or a stored slot value differs when read from the same swapchain handle.

**Possible implementation causes:** The implementation may key private data by the wrong object type or handle, lose slot association, mishandle slot destruction and recreation, or ignore `vkSetPrivateDataEXT`. Android's initial-value exception is excluded from this conclusion.

## Case Pruning

### Requirement-based pruning

- All cases require the platform surface extensions and `VK_KHR_swapchain`.
- Concurrent-sharing creation needs at least two compatible queue families. The image-alias concurrent case also creates a second queue.
- `vkAcquireNextImage2KHR`, image-alias binding, and device-group paths require the relevant device-group functionality. The source checks `VK_KHR_swapchain` revision 69 for structures introduced with that revision. `device_group2` also requires at least two physical devices in the selected group.
- `private_data` requires the `privateData` feature and enables `VK_EXT_private_data`.
- `modify.resize` is registered only when the platform's swapchain extent does not have to match the native window size.
- Multi-swapchain leaves skip when the platform cannot create the requested number of windows. Unsupported image-format/property combinations are skipped before swapchain creation.

These checks remove cases that the selected platform or implementation cannot support legally.

### Design-based pruning

- `private_data` deliberately omits `image_extent`; the other ten creation dimensions cover private-data association without extent-driven allocation pressure.
- `image_sharing_mode` generates only concurrent sharing because exclusive sharing is already the baseline. `exclusive_nonzero_queues` isolates the separate rule that queue-family fields are ignored for exclusive sharing.
- OOM simulation skips generated concurrent-sharing records in its inner allocation loop because its device helper supplies only one queue-family index there.
- OOM simulation bounds work to 300 parameter records and 1024 allocation positions. These bounds control runtime rather than express a Vulkan support limit.
- The creation families vary one field at a time. They do not attempt the Cartesian product of all legal `VkSwapchainCreateInfoKHR` values.

## Key Takeaways

- One implementation file covers eight distinct swapchain contracts, so the direct test family child is the useful behavioral axis.
- Creation values come from surface capabilities. Failures should be interpreted against the exact selected dimension, not as a generic swapchain failure.
- The rendering workload validates acquire, submit, and present plumbing rather than image contents.
- Retirement tests preserve the distinction between acquiring from a retired swapchain, which is invalid, and presenting an image acquired before retirement, which is allowed.
- The `simulate_oom.image_swapchain_create_info*` leaves are ordinary image-alias tests because shared registration adds them without the failing allocator.
- See `## Failure Meaning` for the symptom and cause boundaries of each behavior.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Family registration | [`createSwapchainTests`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2953-L2973) | Registers the eight direct children shown in the hierarchy. |
| Creation dimension names and values | [`TestDimension` and `generateSwapchainParameterCases`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L340-L605) | Defines the generated matrix and its valid baseline. |
| Normal creation | [`createSwapchainTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L619-L739) | Checks image properties, expected OOM pressure cases, and swapchain creation. |
| Private data | [`createSwapchainPrivateDataTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L747-L889) | Implements slot creation, initial-value checks, writes, and readback. |
| Simulated OOM | [`createSwapchainSimulateOOMTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L891-L1005) | Injects failures and validates allocation callbacks. |
| Baseline rendering | [`basicRenderTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1180-L1289) | Contains the 600-frame acquire, submit, and present loop. |
| Swapchain-memory image aliases | [`testImageSwapchainCreateInfo`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1297-L1515) | Creates and binds application images to swapchain memory. |
| Multi-swapchain rendering | [`multiSwapchainRenderTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1632-L1802) | Batches two or ten swapchains into presentation calls. |
| Device-group rendering | [`deviceGroupRenderTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1804-L2015), [`deviceGroupRenderTest2`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2017-L2366) | Implements local and split-instance/remote device-group variants. |
| Resize, image query, lifetime, and acquisition | [`resizeSwapchainTest` through `acquireTooManyTimeoutTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2384-L2868) | Owns the remaining host-side behavior checks. |
| Render workload shaders | [`WsiTriangleRenderer::getPrograms`](../../../framework/vulkan/vkWsiUtil.cpp#L1171-L1194) | Supplies the fixed rotating-triangle workload. |
| Swapchain creation and retirement rules | [Vulkan WSI specification](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L5734-L6045) | Defines image equivalence, creation fields, `oldSwapchain`, and retirement. |
| Image enumeration and acquisition rules | [Vulkan WSI specification](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L6780-L7004) | Defines `VK_INCOMPLETE`, acquisition synchronization, and timeout results. |
| Private-data semantics | [Vulkan private-data specification](../../../../vulkan-docs/src/chapters/private_data.adoc#L136-L213) | Defines set/get behavior, default zero, and the Android erratum. |
| Representative registered leaves | [`vk-default/wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L15387-L15439) | Confirms the representative headless hierarchy in mustpass. |
