# Understanding Brief: WSI incremental present tests

## One-Sentence Test Purpose

This test checks whether a presentation engine accepts a long sequence of partially updated swapchain images when the application supplies matching `VK_KHR_incremental_present` damage rectangles across supported scaling, present-mode, transform, and composite-alpha configurations.

## Background Knowledge

### Incremental-present regions are optimization hints

`VkPresentRegionsKHR` extends `VkPresentInfoKHR` with one `VkPresentRegionKHR` per presented swapchain. Each region contains `VkRectLayerKHR` rectangles that describe image pixels changed since the last presentation to that swapchain. The presentation engine may ignore this hint, so the application must still provide a complete, valid presentable image.

Why it matters here:

- The test renders all updates that an acquired swapchain image missed, then reports the same range of rectangles in the incremental-present variant.
- Rectangles use swapchain-image pixel coordinates and layer 0. The presentation engine accounts for the swapchain transform when it applies them.

### Swapchain image history is per image

Acquisition can return a different swapchain image on each frame. A partially updated image must catch up from the frame after its own previous use rather than from the previous global frame.

Why it matters here:

- `m_imageNextFrames[imageIndex]` records the first update that the acquired image still needs.
- A newly seen image starts with a full-image update. A reused image receives every missed rectangular update before presentation.

## One Concrete Example

Consider `dEQP-VK.wsi.headless.incremental_present.scale_none.fifo.identity.opaque.incremental_present`.

Suppose frame 12 acquires an image last used through frame 9. The command buffer renders the rectangles for frames 10, 11, and 12 into that image. The test then builds three matching `VkRectLayerKHR` entries and chains their `VkPresentRegionKHR` through `VkPresentRegionsKHR` to `VkPresentInfoKHR`. If this is the image's first use, the update range starts at frame 0; frame 0 covers the full image and initializes its contents before later partial draws.

## End-to-End Test Flow

```text
[host] select one scaling, present mode, pre-transform, composite-alpha mode, and leaf behavior
[host] create a surface and a device; enable VK_KHR_incremental_present only for the incremental_present leaf
[host] choose representative surface formats and generate two image extents per selected format
[host] create one swapchain configuration and its image views, framebuffers, render pass, pipeline, semaphores, and fences
[host] acquire a swapchain image and find the first frame update that image still needs
[host] record all missed rectangular draws, using a full-image clear and draw when the image is first used
[device] execute the draw commands and signal the render-complete semaphore
[host] for incremental_present, attach rectangles for the same missed-frame range to VkPresentInfoKHR; for reference, leave pNext null
[host] call vkQueuePresentKHR, check both the command result and per-swapchain result, then wait for the queue to become idle
[host] repeat for 300 frames, then repeat for each generated swapchain configuration
[host] recreate resources after VK_ERROR_OUT_OF_DATE_KHR or VK_SUBOPTIMAL_KHR, with a limit of 20 such retries
[host] report failure for any other Vulkan error or after too many out-of-date/suboptimal results
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- `Programs::init` supplies a fixed vertex shader that emits a full-screen two-triangle quad.
- The fixed fragment shader reads a 32-bit frame index through a push constant and combines it with `gl_FragCoord` bits to produce a frame-dependent RGB pattern.
- The graphics pipeline uses a dynamic scissor. Each frame changes the scissor to the rectangle returned by `getRenderFrameRect`; frame 0 covers the full image.
- `generateSwapchainConfigs` chooses at most one `VK_COLOR_SPACE_SRGB_NONLINEAR_KHR` format and one non-SRGB format, then creates two extent configurations for each selected format.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Swapchain images | yes | yes | device writes | no | Each acquired image retains its own update history and receives the missed rectangles before presentation. |
| Image views and framebuffers | yes | yes | device writes | no | They make each swapchain image the color attachment for partial rendering. |
| 32-bit fragment push constant | yes | yes | device reads | no | It carries the frame index used to vary the pixel pattern. |
| Acquire/render semaphores and submission fences | yes | yes | device waits/signals | host waits/reuses | They order acquisition, rendering, presentation, and command-buffer reuse. |
| `VkPresentRegionsKHR` data | yes | passed through `vkQueuePresentKHR` | presentation engine reads | no | It names the rectangles updated since the acquired image's prior presentation. |

The test has no descriptor sets, sampled images, storage buffers, or host-visible readback image. It does not inspect presented pixels.

## What Is Checked

- Each acquire, queue submission, and presentation call must complete without an unexpected Vulkan error.
- Both `vkQueuePresentKHR` itself and the per-swapchain `pResults[0]` value must pass `VK_CHECK_WSI`.
- The incremental-present leaf must accept the exact nonempty rectangle list attached through `VkPresentRegionsKHR` for each frame.
- Every generated swapchain configuration must complete 300 frames.
- `VK_ERROR_OUT_OF_DATE_KHR` and `VK_SUBOPTIMAL_KHR` trigger resource recreation; more than 20 occurrences for one configuration fail the test.
- The test does not compare the `reference` and `incremental_present` images and does not perform pixel readback. Its verdict covers error-free execution and acceptance of the incremental-present metadata, not visual equivalence.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `reference`, `incremental_present`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `reference` | Baseline surface, swapchain, rendering, synchronization, acquisition, or presentation failure under the selected configuration. |
| `incremental_present` | Baseline presentation failure, or incorrect support for `VK_KHR_incremental_present` structures and updated-region handling under the selected configuration. |

A failure caused only by exceeding the out-of-date/suboptimal retry limit points to unstable surface/swapchain compatibility during the run rather than to a pixel-comparison mismatch.

## Important Variations and Special Cases

- `scale_none` uses the surface's current or selected extent. `scale_up` uses a smaller swapchain image, while `scale_down` uses a larger one within surface limits.
- The source registers `scale_up` and `scale_down` only when platform properties say that swapchain images scale to the window size, and never for Wayland. Current mustpass evidence contains these paths for Android and Metal; the other platform branches contain `scale_none` only.
- The source generates five present-mode intermediate nodes, nine transform nodes, and four composite-alpha nodes. Unsupported values cause `NotSupportedError` rather than a failed execution.
- The `fifo_latest_ready` cases require `VK_EXT_present_mode_fifo_latest_ready`; device creation enables `presentModeFifoLatestReady` when that extension is present.
- The source variable `unusedInfo` names the second extent configuration, but the test later iterates and presents every entry in `m_swapchainConfigs`. It does not create an unused swapchain alongside an active one, and `oldSwapchain` remains `VK_NULL_HANDLE` in these configurations.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Region generation and partial draw | [`getRenderFrameRect`, `getUpdatedRects`, and `cmdRenderFrame`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L227-L285) | Defines the full first update, later damage rectangles, and frame-dependent draw. |
| Per-image catch-up rendering | [`createCommandBuffer`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L287-L330) | Replays every update missed by the acquired image. |
| Configuration generation | [`selectRepresentativeFormats` and `generateSwapchainConfigs`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L576-L719) | Selects formats, extents, and support checks. |
| Resource setup | [`initSwapchainResources`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L780-L817) | Creates per-swapchain rendering and synchronization objects. |
| Frame submission and presentation | [`IncrementalPresentTestInstance::render`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L851-L953) | Shows acquisition, catch-up tracking, submission, both present paths, and result checks. |
| Retry and completion logic | [`IncrementalPresentTestInstance::iterate`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L955-L1035) | Defines 300-frame runs, configuration iteration, and out-of-date handling. |
| Shader programs | [`Programs::init`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1037-L1074) | Supplies the fixed quad and frame-dependent fragment shader. |
| Registration matrix | [`createIncrementalPresentTests`](../../../modules/vulkan/wsi/vktWsiIncrementalPresentTests.cpp#L1078-L1176) | Registers scaling, present mode, transform, alpha, and leaf dimensions. |
| WSI family routing | [`createTypeSpecificTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L74) | Places `incremental_present` below each platform branch. |
| Platform scaling properties | [`getPlatformProperties`](../../../framework/vulkan/vkWsiUtil.cpp#L83-L158) | Explains which platform branches can register scaled cases. |
| Vulkan incremental-present semantics | [`VkPresentRegionsKHR`, `VkPresentRegionKHR`, and `VkRectLayerKHR`](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L7584-L7685) | Defines the hint, coordinate/transform rules, and rectangle validity. |
| Mustpass paths | [`wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L11542) | Confirms executable `wsi.<platform>.incremental_present` paths. |

## Questions / Risk Points for User Audit

- The source and spec support the per-image catch-up model and the transform-relative rectangle semantics.
- The test has no visual oracle; documentation must not claim that it proves displayed pixels match the reference path.
- The misleading local name `unusedInfo` must not be described as a concurrently created, unpresented swapchain.
- Registration varies by platform. The final hierarchy should show one stable platform-qualified family root and its direct scaling child, then document conditional scaled branches separately.

No unresolved point changes the final page's semantics, representative shader choice, or validation claims.

## Conversion Notes for Final Wiki Rewrite

- Keep the optimization-hint and per-image-history concepts as compact Background Knowledge bullets.
- Use the `reference` and `incremental_present` test case leaves as the behavioral axis.
- Preserve the `### Failure Cause Mapping` table above verbatim.
- Use the headless FIFO/identity/opaque incremental-present path for the shader walkthrough. The fragment shader explains how partial rectangles receive visible frame-dependent content; the page must still state that CTS does not read pixels back.
- Keep the runtime section focused on per-image catch-up rendering, matching region construction, 300-frame iteration, and retry behavior.
- Move source navigation and the spec chapter to the final appendix.
