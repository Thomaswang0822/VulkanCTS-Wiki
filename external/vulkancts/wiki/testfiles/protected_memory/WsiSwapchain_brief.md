# Understanding Brief: Protected WSI swapchain tests

## One-Sentence Test Purpose

This test checks whether Vulkan can create and use protected swapchains for supported window-system integration (WSI) platforms across surface-dependent swapchain parameters and a protected rendering loop.

## Background Knowledge

### Protected swapchains and surfaces

A `VkSurfaceKHR` connects Vulkan to a native window, display, or headless presentation target. A protected swapchain sets `VK_SWAPCHAIN_CREATE_PROTECTED_BIT_KHR`, which makes the swapchain images protected. The `VK_KHR_surface_protected_capabilities` query reports whether the particular surface can display protected swapchain images.

Why it matters here:
- The test must query the surface capability before using the protected swapchain flag.
- Surface creation and swapchain behavior vary by WSI type, so the same parameter set is not assumed to work on every platform.

### Protected queues and submissions

Protected work runs through a queue family with `VK_QUEUE_PROTECTED_BIT`. The test creates a protected queue, records rendering in a command pool with `VK_COMMAND_POOL_CREATE_PROTECTED_BIT`, and attaches `VkProtectedSubmitInfo::protectedSubmit = VK_TRUE` to the submission. Acquire and present semaphores connect swapchain ownership with the protected rendering submission.

Why it matters here:
- The create cases test protected swapchain construction without rendering.
- The render case tests the complete acquire, protected submit, and present sequence.

## One Concrete Example

For `dEQP-VK.protected_memory.interaction.wsi.headless.swapchain.render.basic`, the host creates a 256 x 256 native window target, a protected surface, and a protected swapchain with two images. The test acquires one image, records a triangle render pass into a protected command buffer, submits it with `protectedSubmit = VK_TRUE`, and presents the same image. It repeats this for 600 frames. The vertex shader rotates the triangle using a push-constant frame index; the fragment shader writes `(1, 0, 1, 1)`.

## End-to-End Test Flow

```text
[host] select a WSI type and one registered swapchain path
[host] enumerate supported WSI, surface, and optional protected-capability extensions
[host] create a native display/window and a VkSurfaceKHR
[host] create a Vulkan 1.1 protected context with a graphics, compute, surface-capable protected queue
[host] query surface capabilities, formats, present modes, and protected-surface support
[host] create a protected swapchain, or vary one selected VkSwapchainCreateInfoKHR dimension
[host] for the render case, create the triangle pipeline, protected command pool, semaphores, fences, and command buffers
[host] acquire a swapchain image
[device] execute the protected triangle render pass
[host] submit the command buffer with VkProtectedSubmitInfo and present the acquired image
[host] repeat the acquire, submit, and present loop, then wait for the device to become idle
[host] decide pass/fail from Vulkan operation results; an unsupported prerequisite or unavailable protected surface is skipped
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

- The render path generates `tri-vert` and `tri-frag` GLSL programs in `TriangleRenderer::getPrograms` and compiles them into the graphics pipeline.
- The vertex program consumes one `uint` push constant, `frameNdx`, and computes a rotation angle as `frameNdx / 100.0`.
- The fragment program has no inputs and writes a constant magenta color.
- The create path does not generate shaders; it constructs and destroys a swapchain for each selected parameter value.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkSurfaceKHR` and native display/window | yes | used by WSI | consumed by surface and presentation operations | no | Selects the platform-specific presentation target. |
| Protected `VkSwapchainKHR` images | created by WSI from protected swapchain info | framebuffer color attachment | written by the triangle render pass and read by presentation | no | Carries protected rendered content to presentation. |
| Vertex buffer | yes, host-visible and unprotected | vertex binding 0 | read by the vertex stage | no | Supplies the three triangle positions without exposing protected image contents. |
| Push constant `frameNdx` | yes, per draw | vertex push-constant range, offset 0, size 4 | read by the vertex stage | no | Changes the triangle rotation on each frame. |
| Render pass and framebuffers | yes | binds each swapchain image view | color attachment write | no | Routes the render output to the acquired swapchain image. |
| Protected command pool and command buffers | yes | submitted to the protected queue | record and execute draw work | no | Carries the protected rendering commands. |
| Acquire and render-complete semaphores | yes | queue synchronization | signal and wait around acquire, submit, and present | no | Orders image availability, rendering, and presentation. |
| Fences | yes | queue completion tracking | signaled by acquire/submit operations | host waits on them | Limits queued frames and ensures reusable synchronization objects are complete. |

The test does not copy swapchain images back to host memory. The create cases use successful `vkCreateSwapchainKHR` and destruction as their result; the render case treats successful acquire, protected submit, present, and final idle wait as success.

## What Is Checked

- The test verifies that the required WSI extensions can be enabled and that native display/window creation succeeds for the selected WSI type.
- When `VK_KHR_surface_protected_capabilities` is advertised, `VkSurfaceProtectedCapabilitiesKHR::supportsProtected` must be true before the protected swapchain is created.
- Create cases exercise valid values reported by the surface for image count, format, extent, array layers, usage, sharing mode, transform, composite alpha, present mode, and clipping.
- The render case accepts `VK_SUBOPTIMAL_KHR` from image acquisition as a logged condition but checks other failures with `VK_CHECK` or `VK_CHECK_WSI`.
- The render loop executes 600 frames, then waits for device idle. A successful completion returns `Rendering tests succeeded`.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `create`, `render`

`create` varies one `VkSwapchainCreateInfoKHR` dimension and checks protected swapchain creation. `render` uses a fixed basic swapchain and checks the protected acquire, rendering, submission, and presentation sequence. WSI type is an additional platform behavior dimension shared by both families.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `create` | Protected swapchain creation, surface capability handling, WSI extension setup, or the selected `VkSwapchainCreateInfoKHR` parameter is mishandled. |
| `render` | Protected swapchain lifecycle, protected graphics submission, acquire/present synchronization, WSI presentation, or the basic triangle pipeline path is mishandled. |

Failures across both families can also arise from missing protected-memory support, queue-family selection, native display/window setup, or platform-specific WSI availability.

## Important Variations and Special Cases

- The WSI type values are `android`, `direct`, `direct_drm`, `headless`, `metal`, `wayland`, `win32`, `xcb`, and `xlib`. The parent protected-memory dispatcher excludes this branch under Vulkan SC.
- The create family has ten dimensions: `min_image_count`, `image_format`, `image_extent`, `image_array_layers`, `image_usage`, `image_sharing_mode`, `pre_transform`, `composite_alpha`, `present_mode`, and `clipped`.
- The implementation enables `VK_EXT_swapchain_colorspace` when advertised. If `VK_KHR_surface_protected_capabilities` is advertised, it also enables `VK_KHR_get_surface_capabilities2` and queries protected surface support.
- Present-mode cases optionally enable `VK_KHR_shared_presentable_image`. Shared present modes use `minImageCount = 1`; without the extension the corresponding case is skipped.
- Extent cases use fixed candidate sizes `{1,1}`, `{16,32}`, `{32,16}`, `{632,231}`, and `{117,998}` where the platform permits application-selected extents. The implementation clamps candidates to surface limits and avoids cases whose estimated protected image memory would exceed the protected heap.
- Image-count and format/extent cases catch `vk::OutOfMemoryError` while probing protected-heap capacity. If no viable case remains, they return unsupported rather than claiming a functional failure.
- The render path uses a 256 x 256 desired size, a basic protected swapchain, two-times-the-image-count queued-frame budget, and 600 frames.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| WSI extension selection | [getRequiredWsiExtensions](../../../modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp#L82-L121) | Selects platform, display, colorspace, and protected-surface extensions. |
| Native objects and protected context | [NativeObjects](../../../modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp#L124-L171), [ProtectedContext](../../../modules/vulkan/protected_memory/vktProtectedMemContext.cpp#L52-L73) | Creates the platform target, surface, protected device, and queue. |
| Create parameter dimensions | [TestDimension](../../../modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp#L173-L195), [populateSwapchainGroup](../../../modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp#L960-L969) | Defines and registers the ten create dimensions. |
| Create matrix execution | [executeSwapchainParameterCases](../../../modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp#L237-L864) | Varies each dimension, applies support and memory pruning, and creates the swapchain. |
| Create support and protected-surface query | [createSwapchainTest](../../../modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp#L884-L937) | Enables extensions, creates the context, and checks `supportsProtected`. |
| Render pipeline and shaders | [TriangleRenderer](../../../modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp#L1015-L1245) | Creates framebuffers, pipeline, vertex buffer, and the two generated shaders. |
| Protected render loop | [basicRenderTest](../../../modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp#L1286-L1428) | Acquires, submits, presents, and repeats for 600 frames. |
| Test registration | [createSwapchainTests](../../../modules/vulkan/protected_memory/vktProtectedMemWsiSwapchainTests.cpp#L1440-L1473) | Registers WSI types, `swapchain`, `create`, and `render.basic`. |
| Protected support and queue selection | [checkProtectedContextSupport](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L102-L127), [chooseProtectedMemQueueFamilyIndex](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L129-L159) | Defines API, feature, queue, and surface support requirements. |
| Protected submit and command pool | [queueSubmit](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L460-L495), [makeCommandPool](../../../modules/vulkan/protected_memory/vktProtectedMemUtils.cpp#L512-L525) | Defines protected submission and protected command-buffer allocation. |
| WSI registration evidence | [protected-memory.txt](../../../mustpass/main/vk-default/protected-memory.txt#L739-L837) | Lists the WSI create and render paths for all nine WSI types. |
| Protected surface semantics | [VkSurfaceProtectedCapabilitiesKHR](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L3237-L3273) | Defines when a protected swapchain may be displayed for a surface. |
| Protected swapchain semantics | [swapchain protected flag](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L6220-L6298) | Defines the protected swapchain flag and related create-info validity. |

## Questions / Risk Points for User Audit

- Is `create` versus `render` the right primary behavioral axis, with WSI type treated as a secondary platform dimension?
- Should the final page emphasize all nine WSI branches equally, or focus on the platform-independent swapchain behavior and list the branches as registration coverage?
- Does the distinction between `VK_SUBOPTIMAL_KHR` during acquire and other checked WSI results need more explanation?
- Are the protected-heap memory estimates clear enough to distinguish intentional unsupported skips from functional failures?
- Is the vertex shader's push-constant rotation useful to retain in the final walkthrough even though the test's main property is protected presentation?

## Conversion Notes for Final Wiki Rewrite

- Keep `## Background Knowledge` short: explain protected surfaces and protected queue submissions, then move concrete API choices to later sections.
- Use the render case as the representative shader walkthrough because it is the only path with generated shader code and it completes a protected acquire, submit, and present cycle.
- Treat `create` and `render` as the behavior values and copy the failure mapping table unchanged into the final page.
- Explain the ten create dimensions in a compact table, then describe platform-specific extent and present-mode branches under variations or pruning.
- Keep native WSI object details and helper functions in the source appendix unless they explain a failure or platform constraint.
- The shader walkthrough should include the vertex and fragment source, generated SPIR-V for both stages, and a brief note that no shader reads protected memory directly. The render result is observed through successful WSI operations rather than image readback.
