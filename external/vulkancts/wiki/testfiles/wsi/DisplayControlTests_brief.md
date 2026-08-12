# Understanding Brief: `wsi.display_control`

## One-Sentence Test Purpose

This test family exercises display power requests, display and device event registration, and a direct-display presentation loop intended to validate the `VK_SURFACE_COUNTER_VBLANK_EXT` swapchain counter.

## Background Knowledge

### Direct display surfaces and presentation

`VK_KHR_display` exposes physical displays and display planes as Vulkan objects. The counter case does not create a platform window. It selects a display and compatible plane, obtains a display mode, creates a `VkSurfaceKHR` with `vkCreateDisplayPlaneSurfaceKHR`, and presents a swapchain to that surface. The Vulkan specification defines a display surface as one plane in a complete display configuration ([display surfaces](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L2237-L2249)). Creating the surface does not apply the display configuration; presentation does ([display surface creation](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L2267-L2299)).

Why it matters here:
- The counter case needs a `VkDisplayKHR` and a plane that supports it.
- The counter, power, and display-event cases reject the environment if a platform WSI type reports access to a display. The device-event case does not enumerate displays or run that ownership check.

### Event fences and surface counters

`VK_EXT_display_control` can create a fence that a device or display event will signal. `VK_DISPLAY_EVENT_TYPE_FIRST_PIXEL_OUT_EXT` means the first pixel of the next refresh cycle has left the display engine. `VK_DEVICE_EVENT_TYPE_DISPLAY_HOTPLUG_EXT` means a display has been plugged into or unplugged from the device ([event fences](../../../../vulkan-docs/src/chapters/synchronization.adoc#L2882-L2988)). The extension also lets a swapchain enable surface counters through `VkSwapchainCounterCreateInfoEXT`. An enabled counter becomes active when the presentation engine processes the first presentation command ([surface counters](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L6434-L6489)).

Why it matters here:
- The event cases check registration return values and destroy returned fences. They do not wait for an event.
- The counter source contains a range check, but the current iteration boundary prevents execution from reaching it.

## One Concrete Example

Consider `dEQP-VK.wsi.display_control.swapchain_counter` after the test has selected a display plane and created a `VK_PRESENT_MODE_FIFO_KHR` swapchain.

1. The host chains `VkSwapchainCounterCreateInfoEXT` to `VkSwapchainCreateInfoKHR` with `surfaceCounters = VK_SURFACE_COUNTER_VBLANK_EXT`.
2. The host acquires an image, submits a command buffer that draws a fixed orange quad, and presents the image.
3. The iteration loop renders with `m_frameNdx` values 0 through 19, then increments the index to 20 and finishes.
4. `render()` guards the counter query with `m_frameNdx >= m_frameCount`. Since the last call to `render()` sees index 19, the query and its intended inclusive range check, `20 - swapchainImageCount` through `20`, do not run.

The shader supplies presentable work. The source intends to observe the display counter, but the current control flow only exercises swapchain creation and presentation.

## End-to-End Test Flow

```text
1. Counter path
[host] create a custom instance with surface, display, and display-surface-counter extensions
[host] select a display, compatible plane, mode, direct surface, and present-capable queue
[host] create a device with swapchain and display-control extensions
[host] create a FIFO swapchain with the vblank counter enabled
[host] create the fixed quad shaders and rendering resources
[host] acquire, submit, and present 20 frames
[host] recreate swapchain resources after VK_ERROR_OUT_OF_DATE_KHR, up to 10 times
[host] finish after frame index 19 without entering the counter-query branch

2. Display-scoped function paths
[host] enumerate direct displays and reject platform WSI ownership
[host] issue ON, SUSPEND, OFF, ON requests per display and check each result
[host] register one FIRST_PIXEL_OUT fence per display and destroy the fences

3. Device-scoped function path
[host] register one DISPLAY_HOTPLUG fence and destroy it
[host] decide pass/fail from command results
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`SwapchainCounterTestCase::initPrograms` generates two GLSL 4.50 shaders. `quad-vert` computes clip-space positions from `gl_VertexIndex` for a six-vertex triangle-list quad. `quad-frag` writes `vec4(1.0, 0.5, 0.0, 1.0)`. The source supplies no explicit `vk::ShaderBuildOptions`, so the CTS baseline target is SPIR-V 1.0 ([baseline target](../../../framework/vulkan/vkPrograms.cpp#L1048-L1052)). No specialization constants or shader variants change this rendering path.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|---|---:|---:|---:|---:|---|
| Direct display `VkSurfaceKHR` | yes | yes | presentation targets it | no | Connects the swapchain to a display plane. |
| `VkSwapchainKHR` | yes | yes | images are acquired and presented | no in reachable control flow | Enables `VK_SURFACE_COUNTER_VBLANK_EXT`, although the current loop never queries it. |
| Swapchain images and image views | yes | yes | color attachment writes | no | Receive the quad render before presentation. |
| Render pass, pipeline, and framebuffers | yes | yes | define and execute the draw | no | Produce presentable work for the counter path. |
| Acquire and render semaphores, submission fences | yes | yes | synchronize acquire and submission | the host waits on reused submission fences | Keep repeated submissions reusable. |
| Event fences | returned by registration | no queue submission in these cases | a future display or device event can signal them | no wait | The cases check registration success, then destroy the handles. |

## What Is Checked

- `display_power_control` requires `VK_SUCCESS` from `vkDisplayPowerControlEXT` for every available display and for `VK_DISPLAY_POWER_STATE_ON_EXT`, `VK_DISPLAY_POWER_STATE_SUSPEND_EXT`, `VK_DISPLAY_POWER_STATE_OFF_EXT`, and `VK_DISPLAY_POWER_STATE_ON_EXT` in that order.
- `register_display_event` requires `VK_SUCCESS` from `vkRegisterDisplayEventEXT` with `VK_DISPLAY_EVENT_TYPE_FIRST_PIXEL_OUT_EXT` for each available display, then destroys the returned fences.
- `register_device_event` requires `VK_SUCCESS` from `vkRegisterDeviceEventEXT` with `VK_DEVICE_EVENT_TYPE_DISPLAY_HOTPLUG_EXT`, then destroys the returned fence.
- `swapchain_counter` checks setup, acquisition, submission, and presentation across 20 frames. It fails after more than 10 `VK_ERROR_OUT_OF_DATE_KHR` recoveries. The current frame-index boundary prevents the intended `vkGetSwapchainCounterEXT` call and range check from running.

## Behavior Parameter Identification

> **Behavior parameter:** registered test family
>
> **Candidate values:** `swapchain_counter`, `display_power_control`, `register_display_event`, `register_device_event`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `swapchain_counter` | Swapchain setup, acquire, submission, or presentation failure, or more than 10 `VK_ERROR_OUT_OF_DATE_KHR` results. The current loop does not reach the counter-query or range-failure branch. |
| `display_power_control` | A non-success result from one of the requested display power transitions. |
| `register_display_event` | A non-success result while registering the first-pixel-out event fence for an available display. |
| `register_device_event` | A non-success result while registering the display-hotplug event fence. |

## Important Variations and Special Cases

- Only `swapchain_counter` creates a custom instance with `VK_KHR_surface`, `VK_KHR_display`, and `VK_EXT_display_surface_counter`, followed by a custom device with `VK_KHR_swapchain` and `VK_EXT_display_control`.
- The three function cases use the normal CTS context. The power and display-event cases call a common helper that requires at least one display and rejects platform WSI ownership. The device-event case does neither.
- The event cases stop after successful registration and fence destruction. They do not wait for a refresh or hotplug event.
- The power case sleeps for 1000 ms after each state request, including the final return to `ON`.
- The counter path fixes FIFO presentation, 20 frames, the vblank counter, and 10 out-of-date recoveries. It has no registered parameter matrix below the test case leaf.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Custom instance and device | [`createInstance` and `createTestDevice`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L70-L143) | Defines counter-path extension sets and rejects platform WSI display ownership. |
| Display, plane, and surface selection | [`getDisplayAndDisplayPlane` and `createSurface`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L146-L245) | Selects a compatible plane and creates the direct surface. |
| Counter configuration | [`createSwapchainCounterConfig` and `createSwapchainConfig`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L464-L540) | Enables vblank counting and checks support for the fixed FIFO mode. |
| Counter execution and unreachable check | [`render`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L698-L760), [`iterate`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L762-L803) | Shows 20 presentations, the guarded query, and loop termination before the guard can become true. |
| Representative shaders | [`initPrograms`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L822-L840) | Defines the fixed vertex and fragment shaders. |
| Direct-display enumeration | [`getDisplays`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L853-L887) | Finds displays for the function cases and rejects platform WSI ownership. |
| Power control | [`testDisplayPowerControl`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L889-L930) | Defines the state sequence, waits, and return-value checks. |
| Event registration | [`testDisplayEvent` and `testDeviceEvent`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L932-L984) | Defines event types, return-value checks, and fence lifetime. |
| Registration | [`createDisplayControlTests`](../../../modules/vulkan/wsi/vktWsiDisplayControlTests.cpp#L988-L994), [`createWsiTests`](../../../modules/vulkan/wsi/vktWsiTests.cpp#L76-L90) | Registers the four leaves under `wsi.display_control`. |
| Default mustpass | [`wsi.txt`](../../../mustpass/main/vk-default/wsi.txt#L11515-L11518) | Lists all four executable paths. |
| Extension semantics | [display control](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L2181-L2234), [surface counters](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L6434-L6491), [event fences](../../../../vulkan-docs/src/chapters/synchronization.adoc#L2882-L2989) | Grounds the power, counter, and event-fence descriptions. |

## Questions / Risk Points for User Audit

- The counter test's name and source comments describe counter validation, but its final bytes do not call `vkGetSwapchainCounterEXT` because `render()` never sees `m_frameNdx == 20`.
- The event cases validate registration return values only. They do not prove later fence signaling.
- The power case requests `OFF` and then `ON`, so it changes physical display state during execution.
- These cases need a physical direct display and do not suit an ordinary headless CI host.

## Conversion Notes for Final Wiki Rewrite

- Keep the registered test family as the behavioral axis and copy the failure mapping table into the final page without edits.
- State the counter control-flow limitation in the overview, behavior, runtime, failure, pruning, and takeaways sections where it affects interpretation.
- Use the counter vertex shader as the representative walkthrough. Mention the fixed fragment shader without adding a second SPIR-V block.
- Keep direct-display, event-fence, and counter activation concepts as short prerequisites.
- Preserve the limit that event cases do not wait and the fact that function cases do not select a display plane.
