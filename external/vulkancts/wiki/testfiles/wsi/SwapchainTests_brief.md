# Understanding Brief: WSI swapchain tests

## One-Sentence Test Purpose

This test checks whether an implementation handles the `VkSwapchainKHR` lifecycle, image acquisition and presentation, parameter-dependent creation, allocation failure, image enumeration, and private-data association across each supported WSI platform.

## Background Knowledge

### Swapchain ownership and image flow

A swapchain owns an implementation-managed set of presentable images. The application queries those images, acquires an available image index, waits for the acquisition signal before rendering, and submits the image for presentation. The implementation chooses the acquisition order. A zero timeout may return `VK_NOT_READY`; an expired finite timeout returns `VK_TIMEOUT`.

Why it matters here:
- The render tests exercise the acquire, render, and present cycle for one or several swapchains.
- The acquisition-limit tests deliberately hold the maximum guaranteed number of images and then make one more bounded acquisition call.
- The image-query tests check the count-and-array enumeration contract, including `VK_INCOMPLETE`.

### Swapchain retirement

Passing an existing swapchain as `oldSwapchain` retires it, even if creation of the replacement fails. The application cannot acquire more images from the retired swapchain, but it may present images acquired before retirement. Destroying the old swapchain releases its remaining resources.

Why it matters here:
- The resize and destruction cases replace one swapchain with another through `oldSwapchain`.
- `retired_swapchain_present` checks the explicit allowance for presenting an image acquired before retirement.

### Creation parameters come from surface capabilities

`VkSwapchainCreateInfoKHR` combines surface-advertised limits and modes: image count, format and color space, extent, array layers, usage, sharing mode, transform, composite alpha, presentation mode, and clipping. A legal test matrix must derive values from the queried capabilities rather than invent arbitrary unsupported combinations.

Why it matters here:
- `create`, `simulate_oom`, and `private_data` use the same generator to vary one creation dimension at a time from a valid baseline.
- `image_swapchain_create_info` covers application-created images bound to swapchain memory, a separate mechanism available with device-group functionality.

## One Concrete Example

Consider `dEQP-VK.wsi.headless.swapchain.render.basic`:

1. The host creates a surface and a swapchain requesting two images, then queries the actual image handles.
2. For each of 600 frames, `vkAcquireNextImageKHR` returns an image index and signals an image-ready semaphore.
3. A command buffer draws a rotating magenta triangle into that image. Queue submission waits on the acquisition semaphore and signals a rendering-complete semaphore.
4. `vkQueuePresentKHR` waits on the rendering-complete semaphore and presents the acquired image.
5. The case passes when every acquisition, index check, submission, presentation, and final device-idle operation returns an accepted result.

The triangle is a visible workload for exercising swapchain use. Its color and geometry are not compared by this test.

## End-to-End Test Flow

```text
1. Parameterized creation and private-data paths
[host] create the WSI instance, native window, surface, and compatible device
[host] query surface capabilities, formats, and presentation modes
[host] generate valid VkSwapchainCreateInfoKHR subcases for one selected dimension
[host] create each swapchain, or inject deterministic allocation failures for simulate_oom
[host] for private_data, create slots, set per-slot values on the swapchain, and read them back
[host] check API results, private-data values, and allocation-callback records

2. Rendering paths
[host] create one, two, or ten windows, surfaces, and swapchains
[host] query swapchain images and create renderer/synchronization objects
[host] acquire an image with vkAcquireNextImageKHR or vkAcquireNextImage2KHR
[device] wait for acquisition, render the triangle, and signal rendering completion
[host/device] submit one or several swapchains to vkQueuePresentKHR
[host] check global and per-swapchain results, then wait for idle

3. Query, resize, destruction, and acquisition-limit paths
[host] create a baseline surface and swapchain
[host] run the selected operation: short image query, replacement through oldSwapchain, destruction, or repeated acquisition
[host] compare the returned count/result with the operation-specific accepted values
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `WsiTriangleRenderer::getPrograms` supplies a fixed vertex shader and fragment shader to rendering, resize, device-group, multi-swapchain, and image-alias cases. The vertex shader rotates a triangle using a frame-index push constant. The fragment shader outputs magenta.
- `generateSwapchainParameterCases` builds `VkSwapchainCreateInfoKHR` records at runtime from current surface capabilities. It changes one `TestDimension` field from a valid baseline.
- The test does not generate randomized shaders, Amber scripts, or hand-authored SPIR-V assembly.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkSwapchainKHR` and presentable images | yes | yes | rendered and presented in render-related cases | image handles and indices only | They are the objects under test. |
| Native windows and `VkSurfaceKHR` objects | yes | yes | presentation engine uses them | no | They define platform-specific capabilities and presentation targets. |
| Image-ready and rendering-complete semaphores | yes | yes | signaled/waited by acquisition, queues, and presentation | no | They order acquisition, rendering, and presentation. |
| Fences and command buffers | yes | yes | queues execute command buffers and signal fences | fence status is waited by host | They bound the number of queued frames and allow resource reuse. |
| Application-created alias images for swapchain memory | yes | yes | rendered in `image_swapchain_create_info` and `device_group2` | no pixel readback | They test `VkImageSwapchainCreateInfoKHR` and `VkBindImageMemorySwapchainInfoKHR`. |
| Private-data slots | yes | associated with the device and swapchain object | no shader access | yes, through `vkGetPrivateDataEXT` | They check the `VK_EXT_private_data` round trip on a swapchain handle. |
| Allocation callback recorder/failing allocator | yes | no | no | host inspects callback records | It injects allocation failures and detects invalid callback behavior or leaks. |

## What Is Checked

- `create` accepts generated, capability-derived creation records. Unsupported image-format/property combinations are skipped after `vkGetPhysicalDeviceImageFormatProperties`; expected pressure cases may report out-of-memory without failing the case.
- `simulate_oom` repeatedly advances the first failing allocation until swapchain creation succeeds or the bounded callback limit produces a quality warning, then validates the allocation callback record for unmatched or invalid operations.
- `render` checks API return values, acquired indices, queue submissions, global presentation results, and per-swapchain presentation results. It does not compare rendered pixels.
- `modify.resize` creates and renders three capability-clamped extents, using each previous swapchain as `oldSwapchain`.
- `destroy` checks null-handle destruction, replacement and destruction of old swapchains, replacement after acquisition, and accepted presentation results from an image acquired before retirement.
- `get_images.incomplete` checks `VK_INCOMPLETE`, the returned count, and that entries outside the reported range remain untouched. `get_images.count` checks count stability between the count-only and array queries.
- `acquire.too_many` accepts `VK_SUCCESS`, `VK_SUBOPTIMAL_KHR`, or `VK_NOT_READY` for the extra zero-timeout request. `acquire.too_many_timeout` accepts `VK_SUCCESS`, `VK_SUBOPTIMAL_KHR`, or `VK_TIMEOUT` for the extra finite-timeout request.
- `private_data` checks initial zero where required, writes `i * i * i + 1` to 100 slots, reads each value back, and repeats after recreating the slots. Android skips the initial-zero assertion because of the specification erratum for swapchain objects.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `create`, `simulate_oom`, `render`, `modify`, `destroy`, `get_images`, `acquire`, `private_data`

## What Failure Means

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

## Important Variations and Special Cases

- The same swapchain hierarchy is registered below each WSI platform. Available leaves still depend on platform properties and mustpass selection.
- `create` and `simulate_oom` both register `image_swapchain_create_info` and `image_swapchain_create_info_concurrent` because both use `populateSwapchainGroup`. Those two leaves call `testImageSwapchainCreateInfo` directly, so the copies under `simulate_oom` do not inject allocation failures.
- `private_data` omits `image_extent`. Its other ten dimension leaves reuse the normal creation matrix before testing private data.
- `modify.resize` is registered only when the platform does not require the swapchain extent to match the native window size.
- Concurrent-sharing paths require at least two compatible queue families. Device-group cases require device-group support; `device_group2` also requires at least two physical devices in the selected group.
- Basic rendering runs 600 frames. Multi-swapchain rendering runs `180 * swapchainCount` frames. The image-alias case and each resize extent run 60 frames.
- OOM simulation examines at most 300 generated parameter records and at most 1024 first-failing-allocation positions per record.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and family routing | [`createSwapchainTests`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2953-L2973) | Registers all eight behavior families. |
| Creation matrix | [`TestDimension` and `generateSwapchainParameterCases`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L340-L605) | Defines exact dimensions and capability-derived values. |
| Normal creation and private data | [`createSwapchainTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L619-L739), [`createSwapchainPrivateDataTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L747-L889) | Contains the creation result checks and private-data round trip. |
| Allocation failure injection | [`createSwapchainSimulateOOMTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L891-L1005) | Defines bounds, injected failures, warnings, and callback validation. |
| Baseline render loop | [`basicRenderTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1180-L1289) | Shows acquisition, synchronization, drawing, and presentation across 600 frames. |
| Swapchain-memory image aliases | [`testImageSwapchainCreateInfo`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1297-L1515) | Creates application images and binds them to swapchain memory. |
| Multi-swapchain rendering | [`multiSwapchainRenderTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1632-L1802) | Presents one accumulated image per swapchain and checks per-swapchain results. |
| Device-group rendering | [`deviceGroupRenderTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L1804-L2015), [`deviceGroupRenderTest2`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2017-L2366) | Covers local and remote/split-instance device-group paths. |
| Resize, query, lifetime, and acquisition checks | [`resizeSwapchainTest` through `acquireTooManyTimeoutTest`](../../../modules/vulkan/wsi/vktWsiSwapchainTests.cpp#L2384-L2868) | Implements the non-creation/non-render family checks. |
| Fixed render shaders | [`WsiTriangleRenderer::getPrograms`](../../../framework/vulkan/vkWsiUtil.cpp#L1171-L1194) | Shows that shader logic is only the workload used by swapchain operations. |
| Swapchain specification | [WSI swapchain creation and retirement](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L5734-L6045) | Defines creation, image equivalence, `oldSwapchain`, and retirement semantics. |
| Image query and acquisition specification | [WSI image enumeration and acquisition](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L6780-L7004) | Defines `VK_INCOMPLETE`, acquisition signals, and timeout results. |
| Private-data specification | [Private-data set/get semantics](../../../../vulkan-docs/src/chapters/private_data.adoc#L136-L213) | Defines the data association, default zero, and Android swapchain erratum. |
| Representative mustpass evidence | [`vk-default/wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L15387-L15439) | Lists the headless swapchain leaves used as the representative registration branch. |

## Questions / Risk Points for User Audit

- Is grouping by the eight direct test families the clearest behavior axis for this source file?
- Is it clear that the render shaders provide workload but are not themselves validated?
- Does the explanation distinguish OOM simulation from the two image-alias leaves that are also registered below `simulate_oom`?
- Are the platform-dependent registration and support conditions separated from actual failures?

The inspected source, specification, and mustpass evidence resolve these questions for the final rewrite. One source-level caveat remains worth stating: the two `image_swapchain_create_info` leaves under `simulate_oom` execute the ordinary image-alias helper and therefore do not perform OOM simulation.

## Conversion Notes for Final Wiki Rewrite

- Keep swapchain image flow, retirement, and capability-derived creation as short prerequisite bullets.
- Use the eight direct test families as `## Behavior Parameters` values.
- Copy the `### Failure Cause Mapping` table unchanged.
- Explain the host-side workload in `## Runtime Execution and Result Checking`; do not add a representative shader walkthrough because shader behavior is not the tested property and no pixels are compared.
- Preserve the `simulate_oom.image_swapchain_create_info*` caveat and platform-dependent `modify.resize` registration in `## Case Pruning`.
- Move audit-oriented links to the final source appendix.
