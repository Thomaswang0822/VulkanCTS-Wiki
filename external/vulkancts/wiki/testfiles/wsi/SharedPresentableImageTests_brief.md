# Understanding Brief: WSI shared presentable image tests

## One-Sentence Test Purpose

This test checks whether an implementation can render repeatedly to one acquired shared presentable swapchain image, use the required shared image layout, and follow the demand-refresh or continuous-refresh presentation contract without Vulkan or CTS errors.

## Background Knowledge

### Shared presentable images

A swapchain that uses either shared present mode has one presentable image. The application and presentation engine may access that image concurrently after the first presentation. Unlike an ordinary swapchain loop, the application acquires this image once rather than acquiring a different available image for each frame.

Why it matters here:

- The swapchain must use `minImageCount = 1`.
- Rendering and presentation refer to image index `0` throughout the test.
- The presentation engine may read the image while the application updates it.

### Shared present layout and refresh policy

A shared presentable image uses `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR` for supported image operations. The application initially transitions the acquired image to this layout and does not transition it away while rendering and presentation continue.

The refresh policy determines when a presentation request is required. Demand refresh requires a new request to guarantee that the presentation engine uses updated contents. Continuous refresh requires one initial request, after which the presentation engine refreshes from the shared image without further requests.

## One Concrete Example

Consider `dEQP-VK.wsi.headless.shared_presentable_image.scale_none.identity.opaque.demand`.

The host creates a one-image swapchain with `VK_PRESENT_MODE_SHARED_DEMAND_REFRESH_KHR`, acquires image index `0`, and transitions that image to `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR`. For each of 300 frames, it records a draw using the frame index as a fragment-shader push constant, submits the draw, and calls `vkQueuePresentKHR` after the render semaphore signals. It also calls `vkGetSwapchainStatusKHR` after each frame. The case passes if all configurations and frames complete without a collected error. It does not read pixels back or compare the displayed pattern.

## End-to-End Test Flow

```text
[host] select WSI platform, scaling, transform, composite alpha, and shared present mode
[host] query surface formats, modes, capabilities, and shared-present usage flags
[host] build one swapchain configuration for each usable surface format
[host] create a one-image swapchain, render pass, pipeline, image view, framebuffer, semaphores, fences, and command buffers
[host] acquire the single image and verify that its index is 0
[host] transition the image once to VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR
[host] for each of 300 frames, record a draw with the frame index push constant
[device] render 16 quads into the shared image while it remains in the shared-present layout
[host] for demand refresh, present after every draw; for continuous refresh, present only after the first draw
[host] query swapchain status after every frame
[host] recycle per-frame synchronization objects and command buffers across six slots
[host] recreate swapchain resources after VK_ERROR_OUT_OF_DATE_KHR, subject to the retry limit
[host] advance through all usable surface-format configurations and return the collected result
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`Programs::init` adds one vertex shader and one fragment shader. The vertex shader generates quad positions from `gl_VertexIndex` and passes a flat quad index. The fragment shader combines the quad index, frame index, and fragment coordinates to produce a changing color pattern. The pipeline has a four-byte fragment-stage push-constant range for the frame index.

The shaders provide a changing graphics workload. Their output is not read back or compared, so shader arithmetic is not the property under test.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| One-image `VkSwapchainKHR` | yes | yes | presentation engine and rendering use it | no | Owns the single shared presentable image and selects the shared present mode. |
| Swapchain `VkImage` at index `0` | obtained from swapchain | yes | color-attachment writes; presentation-engine reads | no | The application acquires it once and keeps it in `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR`. |
| `VkImageView` and `VkFramebuffer` | yes | yes | used by the graphics pipeline | no | Attach the shared image to the render pass. |
| Render pass | yes | yes | device executes it | no | Uses load/store operations and the shared-present layout as both initial and final layout. |
| Graphics pipeline and shader modules | yes | yes | device executes them | no | Produce changing rendered contents without serving as an oracle. |
| Four-byte push constant | yes | yes | fragment shader reads it | no | Supplies `frameNdx` so successive draws change the pattern. |
| Six fences and six render semaphores | yes | yes | queue operations signal or wait on them | host waits on fences | Bound the number of outstanding submissions and order presentation after rendering when a present occurs. |
| Six command-buffer slots | yes | yes | device executes them | no | Rotate across frames and are freed after their fences complete. |

## What Is Checked

- `VkSharedPresentSurfaceCapabilitiesKHR::sharedPresentSupportedUsageFlags` includes `VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT`.
- The acquired shared image index equals `0`.
- Swapchain creation, acquisition, the initial transition, rendering submissions, presentation requests, fence operations, and status queries return accepted results.
- `demand` issues a presentation request after every rendered frame; `continuous` issues one on frame zero.
- Each usable surface-format configuration completes 300 frames.
- An out-of-date swapchain can be rebuilt until the retry count reaches 20. A later `VK_ERROR_OUT_OF_DATE_KHR` records failure.
- There is no pixel readback, screenshot comparison, or presentation-timing measurement.

## Behavior Parameter Identification

> **Behavior parameter:** present mode test case leaf
>
> **Candidate values:** `demand`, `continuous`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `demand` | Per-frame demand-refresh presentation, render-to-present synchronization, shared-image layout use, swapchain status, or common shared-swapchain lifecycle failure. |
| `continuous` | Initial continuous-refresh presentation, continued rendering without later presentation requests, shared-image layout use, swapchain status, or common shared-swapchain lifecycle failure. |

## Important Variations and Special Cases

- `scale_none` is always registered. `scale_up` and `scale_down` are registered only for WSI types whose platform properties report swapchain extents scaled to the window size.
- Current mustpass evidence includes all three scaling values for `android` and `metal`; the other listed WSI platforms contain `scale_none` cases.
- Nine surface-transform values and four composite-alpha values are registered. Unsupported values cause a not-supported result before execution.
- The source builds a swapchain configuration for each reported surface format whose image format supports the selected usage.
- A `VK_ERROR_OUT_OF_DATE_KHR` from presentation or status checking returns control to `iterate`, which rebuilds resources and restarts the current configuration at frame zero. Other Vulkan errors fail the current configuration and move to the next one.
- The test stresses legal shared-present operation but does not verify which pixels the presentation engine displayed or when it displayed them.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Per-platform registration | [createTypeSpecificTests](../../../modules/vulkan/wsi/vktWsiTests.cpp#L50-L73) | Registers `shared_presentable_image` under each applicable WSI platform. |
| Parameter registration | [createSharedPresentableImageTests](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L964-L1044) | Defines scaling, transform, alpha, and present-mode identifiers. |
| Swapchain configuration | [generateSwapchainConfigs](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L477-L575) | Selects extents, checks support, sets one image, and iterates surface formats. |
| Shared usage capabilities | [getPhysicalDeviceSurfaceCapabilities](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L577-L600) | Queries shared-present usage and requires color-attachment support. |
| Resource initialization | [initSwapchainResources](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L663-L735) | Creates image-dependent objects, acquires image zero, and performs the one layout transition. |
| Per-frame behavior | [render](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L754-L834) | Shows submission, mode-dependent presentation, fences, semaphores, and status queries. |
| Recovery and result | [iterate](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L836-L916) | Implements frame/configuration iteration and out-of-date recovery. |
| Shader workload | [Programs::init](../../../modules/vulkan/wsi/vktWsiSharedPresentableImageTests.cpp#L918-L960) | Generates the changing quad pattern that drives color-attachment writes. |
| Shared present semantics | [Vulkan WSI shared present modes](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L4392-L4414) | Defines demand and continuous refresh behavior. |
| Shared image operation | [Vulkan shared presentable image behavior](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L5652-L5689) | Defines one-time acquisition, concurrent access, and presentation requirements. |
| Shared layout | [Vulkan image layout rules](../../../../vulkan-docs/src/chapters/resources.adoc#L5423-L5429) | Restricts `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR` to shared presentable images and supported uses. |
| Current mustpass coverage | [wsi.txt](../../../mustpass/main/vk-default/wsi.txt#L4129-L4344) | Provides concrete registered paths for the parameter matrix. |

## Questions / Risk Points for User Audit

- Is the distinction between API-flow conformance and visual refresh verification explicit enough?
- Does the present-mode leaf make sense as the primary behavioral axis, with scaling, transform, alpha, format, and WSI platform treated as configuration dimensions?
- Is the one-time acquisition and persistent `VK_IMAGE_LAYOUT_SHARED_PRESENT_KHR` lifetime clear?
- Is out-of-date recovery described without implying that an out-of-date event itself is a conformance failure?

No unresolved source question changes the final page semantics. The fixed count of 300 frames has no stated timing rationale in the source, so the final page should describe it as a fixed workload rather than as five seconds of presentation.

## Conversion Notes for Final Wiki Rewrite

- Keep shared-image concurrency and persistent layout as the only Background Knowledge topics.
- Carry `demand` and `continuous` into `## Behavior Parameters` as the primary axis.
- Copy the `### Failure Cause Mapping` table unchanged.
- Explain the changing shader workload briefly under `## Shader Analysis`; do not add a representative walkthrough because shader output is not checked and shader logic is not the tested behavior.
- Preserve the 300-frame loop, six synchronization slots, per-frame status query, and out-of-date retry behavior in the runtime section.
- Put detailed source navigation in the final appendix.
