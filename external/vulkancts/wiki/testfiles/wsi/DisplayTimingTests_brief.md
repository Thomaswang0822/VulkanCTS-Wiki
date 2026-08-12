# Understanding Brief: `wsi.*.display_timing`

## One-Sentence Test Purpose

This test checks how a swapchain presents rendered frames with and without `VK_GOOGLE_display_timing`, including desired presentation times, returned presentation records, present-mode differences, and recovery from an out-of-date swapchain.

## Background Knowledge

### Desired and past presentation times

`VK_GOOGLE_display_timing` adds two related operations to swapchain presentation:

- An application can attach `VkPresentTimesInfoGOOGLE` to `VkPresentInfoKHR`. Each `VkPresentTimeGOOGLE` supplies a `presentID` and a `desiredPresentTime`, which tells the presentation engine not to display that image before the requested time.
- The application can query `vkGetPastPresentationTimingGOOGLE` for records that have become available. Each record identifies the present and reports `desiredPresentTime`, `actualPresentTime`, `earliestPresentTime`, and `presentMargin`.

The extension expresses these times in nanoseconds against a monotonically increasing clock. Timing records arrive after presentation because the presentation engine works asynchronously.

### Refresh duration and present modes

`vkGetRefreshCycleDurationGOOGLE` reports the duration between refresh-cycle starts. The test uses this value as its initial target image-present duration and changes the target between one and two refresh cycles in response to returned timing records.

The specification defines the full extension behavior for `VK_PRESENT_MODE_FIFO_KHR`. Other present modes permit different handling. `VK_PRESENT_MODE_IMMEDIATE_KHR` may ignore a nonzero desired time, `VK_PRESENT_MODE_MAILBOX_KHR` may replace an image before display, and late `VK_PRESENT_MODE_FIFO_RELAXED_KHR` presents may follow FIFO or immediate-style timing behavior.

## One Concrete Example

For a representative case, use:

```text
dEQP-VK.wsi.headless.display_timing.fifo.display_timing
```

The test creates a FIFO swapchain, obtains its refresh duration, and renders 300 frames. After it starts receiving timing history, it schedules each next target from the preceding target plus the current target image-present duration. Present ID 80 gets a requested time one second earlier than the normal schedule while subsequent targets stay on that schedule. If the returned record classifies present ID 80 as late, the test requires the lateness beyond one refresh cycle to exceed half a second.

The test also checks every returned timing record against the host timestamp captured before `vkQueuePresentKHR`. An `actualPresentTime` earlier than that timestamp is impossible for the recorded call and fails the case.

## End-to-End Test Flow

```text
[host] select a WSI platform, present mode, and reference or display_timing test case
[host] create the surface, device, swapchain, render pass, pipeline, synchronization objects, and per-image views/framebuffers
[host] for display_timing, query the refresh-cycle duration and initialize timing state
[host] acquire a swapchain image and record commands for a frame-dependent color pattern
[device] render the pattern into the acquired swapchain image
[host] for display_timing, query newly available past-presentation records and inspect their timestamps
[host] submit rendering, then present with or without VkPresentTimesInfoGOOGLE
[host] recycle semaphores and fences, repeat for 300 frames, and recreate swapchain resources after VK_ERROR_OUT_OF_DATE_KHR
[host] return the accumulated result after the run or after an unrecoverable error
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

`Programs::init` adds a fixed vertex shader and fragment shader to the CTS source collection. The vertex shader generates full-screen triangles from `gl_VertexIndex`. The fragment shader combines the frame index and fragment coordinates into a changing color pattern. The shaders make successive swapchain images visible, but neither shader measures time or contributes a timing validation result.

The graphics pipeline also has a four-byte fragment-stage push-constant range. The command buffer writes the current frame index into that range before drawing 16 quads.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Swapchain images | yes | yes | fragment output writes them | no | The presentation engine displays these images and produces timing records for their presents. |
| Per-image image views and framebuffers | yes | yes | used as color attachments | no | They connect each acquired swapchain image to the render pass. |
| Frame-index push constant | yes | yes | fragment shader reads it | no | It changes the rendered pattern each frame; it does not carry timing data. |
| Acquire/render semaphores and six fences | yes | yes | queue operations signal or wait on them | host waits on fences | They order acquisition, drawing, presentation, and command-buffer reuse. |
| `m_queuePresentTimes` | yes, host memory | no | no | host reads it | It maps each `presentID` to the host timestamp sampled before `vkQueuePresentKHR`. |
| Returned `VkPastPresentationTimingGOOGLE` records | filled by the implementation | no shader binding | presentation engine produces them | yes | The host uses their timestamps for timing checks and frame-rate adaptation. |

## What Is Checked

The `reference` test case checks that the common rendering and presentation loop completes for the selected present mode. It presents through an ordinary `VkPresentInfoKHR` and performs no timing-record checks.

The `display_timing` test case checks the following:

- Each returned `actualPresentTime` must not precede the host timestamp captured before the matching `vkQueuePresentKHR` call.
- A returned record counts as late when `actualPresentTime` exceeds `desiredPresentTime + refreshDuration + 1 ms`.
- If present ID 80 enters that late branch in `fifo`, `fifo_relaxed`, or `immediate`, its excess beyond one refresh cycle must exceed 0.5 seconds.
- A record counts as capable of earlier presentation when `actualPresentTime > earliestPresentTime` and `presentMargin > 2 ms`. This observation changes the target image-present duration but does not itself fail the case.
- Vulkan call failures enter the result collector. `VK_ERROR_OUT_OF_DATE_KHR` triggers resource recreation up to 20 times; another occurrence fails the case.

The source does not compare rendered pixels, require a timing record for every submitted present, or add a final assertion that present ID 80 appeared in the returned history. Those limits matter when interpreting a pass.

## Behavior Parameter Identification

> **Behavior parameter:** test case leaf
>
> **Candidate values:** `reference`, `display_timing`

The present-mode intermediate node changes the presentation semantics and whether the deliberate present-ID-80 perturbation is used, but the test case leaf selects the primary behavior: baseline presentation or extension-driven scheduling and timing checks.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `reference` | Common WSI setup, rendering, synchronization, acquisition, presentation, or swapchain-recreation failure. |
| `display_timing` | A common WSI-path failure, incoherent returned presentation timestamps, an insufficient late-present interval for the checked present-ID-80 record, or a `VK_GOOGLE_display_timing` query/presentation failure. |

## Important Variations and Special Cases

- The source registers `fifo`, `fifo_relaxed`, `immediate`, `mailbox`, and `fifo_latest_ready`. Each present-mode intermediate node contains `reference` and `display_timing` test cases.
- The present-ID-80 perturbation applies to `fifo`, `fifo_relaxed`, and `immediate`. The source excludes `mailbox` and `fifo_latest_ready`, where queued images may be replaced.
- The test asks the surface to support the selected present mode. Unsupported modes produce `NotSupportedError` before execution.
- Although the `reference` device enables only `VK_KHR_swapchain`, the source's extension-support loop checks both `VK_KHR_swapchain` and `VK_GOOGLE_display_timing` for both leaves. The reference case therefore also requires advertised `VK_GOOGLE_display_timing` support in this implementation.
- A run covers 300 frames and uses six fences to limit work in flight. Swapchain recreation resets the frame index and timing state.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Device extension selection | [createDeviceWithWsi](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L105-L136) | Shows which extensions each leaf enables and which extensions the support loop checks. |
| Swapchain and timing-state initialization | [DisplayTimingTestInstance::initSwapchainResources](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L638-L687) | Creates per-swapchain resources and obtains `refreshDuration`. |
| Timing-record inspection | [DisplayTimingTestInstance::render](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L737-L887) | Contains timestamp consistency, late/early classification, and target-duration adaptation. |
| Timed and reference presentation | [presentation branches](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L905-L975) | Builds `VkPresentTimesInfoGOOGLE`, injects the present-ID-80 case, or uses ordinary presentation. |
| Completion and out-of-date handling | [DisplayTimingTestInstance::iterate](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L986-L1046) | Defines recreation and final result behavior. |
| Shader programs | [Programs::init](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L1048-L1085) | Shows that shaders produce changing frame content but no timing result. |
| Test registration | [createDisplayTimingTests](../../../modules/vulkan/wsi/vktWsiDisplayTimingTests.cpp#L1089-L1124) | Defines present-mode intermediate nodes and the two leaves. |
| Present timing query semantics | [Vulkan WSI specification](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L5293-L5465) | Defines refresh duration, returned timing fields, and present-mode differences. |
| Desired presentation time | [Vulkan WSI specification](../../../../vulkan-docs/src/chapters/VK_KHR_surface/wsi.adoc#L8077-L8141) | Defines `VkPresentTimesInfoGOOGLE` and `VkPresentTimeGOOGLE`. |
| Mustpass paths | [default WSI mustpass list](../../../mustpass/main/vk-default/wsi.txt#L11528-L11537) | Confirms the representative `headless` hierarchy and registered leaves. |

## Questions / Risk Points for User Audit

- The source resolves the primary behavior axis as `reference` versus `display_timing`; present mode remains a secondary dimension.
- The source confirms that the shader only supplies visible, changing frame content, so the final page should not add a representative shader or SPIR-V walkthrough.
- The final page should state the limits of the host checks: it does not require one returned timing record per present or assert at the end that present ID 80 was observed.
- No unresolved semantic risk remains after checking the implementation, mustpass hierarchy, and WSI specification.

## Conversion Notes for Final Wiki Rewrite

- Keep the monotonic-clock, refresh-duration, and returned-timing-field concepts in `Background Knowledge`.
- Use `reference` and `display_timing` as the `Behavior Parameters` subsections.
- Copy the `Failure Cause Mapping` table without changes.
- Explain the present-ID-80 perturbation and adaptive multiplier in the runtime section.
- Keep the shaders in a short `Shader Analysis` explanation because they do not implement timing behavior; do not add a walkthrough or SPIR-V subsection.
- Preserve the validation limits and unconditional extension-support check as bounded source-level caveats.
