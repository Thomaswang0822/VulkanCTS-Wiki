# Understanding Brief: Synchronization smoke tests

## One-Sentence Test Purpose

This test checks whether basic fence, cross-queue semaphore, and equal-index queue-family barrier operations complete with the expected host-visible state or data under the legacy and synchronization2 APIs.

## Background Knowledge

### Execution dependencies and memory dependencies

A semaphore orders queue work across submissions, while a fence reports queue completion to the host. A pipeline barrier can establish execution and memory dependencies inside a command buffer. These mechanisms solve different synchronization problems even when the test uses them around similar rendering or transfer work.

Why it matters here:
- the fence case checks host-visible fence states and wait results;
- the semaphore cases check a signal on one queue followed by a wait on another queue;
- the barrier cases check that transfer or rendering results become visible to host readback.

### Equal queue-family indices

A buffer or image memory barrier uses source and destination queue-family indices for ownership transfer only when the indices differ. These smoke cases deliberately put the same value in both fields. The test covers `VK_QUEUE_FAMILY_IGNORED`, external and foreign special values, and `0xDEADBEEF` to check that equal indices do not trigger an ownership transfer.

Why it matters here:
- the special value changes, but the source and destination values remain equal;
- data correctness after the barrier is the observable result.

## One Concrete Example

For `dEQP-VK.synchronization2.smoke.queue_type_ignore_buffer_external`, the host initializes a 64-element buffer to zero. The command buffer fills every element with `0xAABBCCDD`, then records a `VkBufferMemoryBarrier2` whose source and destination queue-family indices are both `VK_QUEUE_FAMILY_EXTERNAL`. After submission, the host invalidates the allocation and checks all 64 elements.

## End-to-End Test Flow

```text
1. Fence behavior
[host] create two unsignaled fences and record rendering work
[host] submit the work with the first fence
[host] check finite and infinite waits, and require a timeout for the unsubmitted fence
[device] finish the submitted rendering work and signal the first fence
[host] require the submitted fence to report VK_SUCCESS

2. Semaphore behavior
[host] create a device exposing two graphics queues from one queue family
[host] create a binary or timeline semaphore and two rendering command buffers
[device] queue 0 executes the first command buffer and signals the semaphore
[host] wait for the first submission fence
[device] queue 1 waits on the semaphore and executes the second command buffer
[host] wait for the second submission fence and log both readback images

3. Equal-index buffer barrier behavior
[host] create and clear a host-visible buffer
[device] fill the buffer, then execute a legacy or synchronization2 buffer barrier
[host] invalidate the allocation and compare every word with 0xAABBCCDD

4. Equal-index image barrier behavior
[host] create a 1x1 image and readback buffer
[device] transition and clear the image, render blue, transition for transfer, and copy to the buffer
[host] compare the copied pixel with exact blue
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The fence and semaphore cases load a pass-through vertex shader and a fragment shader that writes red. The image barrier cases load a full-screen triangle vertex shader and a fragment shader that writes blue. The shader logic provides observable rendering work; it does not implement the synchronization property.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Fence render target and readback buffer | yes | yes | written | yes, for logging | Supplies device work associated with the fence signal. |
| Two semaphore render targets and readback buffers | yes | yes | written | yes, for logging | Supply distinct work before and after the semaphore dependency. |
| 64-word buffer | yes | yes | written | yes | Detects missing transfer-to-host visibility in the buffer barrier cases. |
| 1x1 image and readback buffer | yes | yes | written | yes | Detects incorrect image transitions, barriers, rendering, or copyback. |
| Semaphore | yes | yes | signaled and waited | no | Orders the two queue submissions. |
| Fences | yes | yes | signaled | host queries and waits | Expose submission completion to the host. |

## What Is Checked

- `fences` requires both new fences to start unsignaled, accepts `VK_SUCCESS` or `VK_TIMEOUT` for zero and two-second waits on submitted work, requires the infinite wait to succeed, requires the unsubmitted fence wait to time out, and requires the submitted fence to report signaled.
- `binary_semaphores` and `timeline_semaphores` require both queue submissions and their fence waits to succeed. The images are logged, not compared against a reference.
- Each buffer case requires all 64 words to equal `0xAABBCCDD`.
- Each image case requires the copied 1x1 pixel to equal blue `(0, 0, 1, 1)` with a zero threshold.

## Behavior Parameter Identification

> **Behavior parameter:** behavior leaf
>
> **Candidate values:** `fences`, `binary_semaphores`, `timeline_semaphores`, `queue_type_ignore_buffer_ignored`, `queue_type_ignore_buffer_external`, `queue_type_ignore_buffer_foreign`, `queue_type_ignore_buffer_arbitrary`, `queue_type_ignore_image_ignored`, `queue_type_ignore_image_external`, `queue_type_ignore_image_foreign`, `queue_type_ignore_image_arbitrary`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fences` | Incorrect initial fence state, wait result, timeout behavior, or queue-completion signal. |
| `binary_semaphores` | Binary semaphore signal/wait submission failure or failure to complete either queue submission. |
| `timeline_semaphores` | Timeline value-1 signal/wait submission failure or failure to complete either queue submission. |
| `queue_type_ignore_buffer_ignored` | Incorrect equal-index handling for `VK_QUEUE_FAMILY_IGNORED`, or missing transfer-to-host visibility. |
| `queue_type_ignore_buffer_external` | Incorrect equal-index handling for `VK_QUEUE_FAMILY_EXTERNAL`, or missing transfer-to-host visibility. |
| `queue_type_ignore_buffer_foreign` | Incorrect equal-index handling for `VK_QUEUE_FAMILY_FOREIGN_EXT`, or missing transfer-to-host visibility. |
| `queue_type_ignore_buffer_arbitrary` | Incorrect equal-index handling for `0xDEADBEEF`, or missing transfer-to-host visibility. |
| `queue_type_ignore_image_ignored` | Incorrect equal-index image-barrier handling for `VK_QUEUE_FAMILY_IGNORED`, layout transition, rendering, or copyback. |
| `queue_type_ignore_image_external` | Incorrect equal-index image-barrier handling for `VK_QUEUE_FAMILY_EXTERNAL`, layout transition, rendering, or copyback. |
| `queue_type_ignore_image_foreign` | Incorrect equal-index image-barrier handling for `VK_QUEUE_FAMILY_FOREIGN_EXT`, layout transition, rendering, or copyback. |
| `queue_type_ignore_image_arbitrary` | Incorrect equal-index image-barrier handling for `0xDEADBEEF`, layout transition, rendering, or copyback. |

## Important Variations and Special Cases

- `synchronization.smoke` contains `fences`; `synchronization2.smoke` does not.
- The two semaphore leaves use the same rendering flow but select binary or timeline semaphore creation and submission values.
- Shared leaves select either legacy submission and barrier commands or synchronization2 wrappers and barrier structures.
- External and foreign queue-family values require their corresponding extensions.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Shader payload and custom two-queue device | [shader and device setup](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L73-L220) | Defines the semaphore configuration, graphics payload, extensions, and queue requirement. |
| Fence checks | [`testFences()`](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1054-L1151) | Defines every checked fence result. |
| Semaphore flow | [`testSemaphores()`](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1154-L1283) | Defines signal/wait submissions and completion checks. |
| Queue-family values and support gates | [family selection and support](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1296-L1355) | Maps registered suffixes to exact values and extensions. |
| Buffer result check | [`ignoreQueueFamilyTypeBuffer()`](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1393-L1489) | Defines barrier variants and word comparison. |
| Image result check | [`ignoreQueueFamilyTypeImage()`](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1492-L1709) | Defines transitions, draw, copyback, and exact pixel comparison. |
| Registration | [both smoke factories](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1725-L1781) | Shows the legacy-only fence leaf and shared leaf matrix. |

## Questions / Risk Points for User Audit

- Is the distinction between synchronization correctness checks and shader payload clear?
- Is `behavior leaf` the useful primary axis for failure diagnosis?
- Is it clear that the semaphore images are logged but not compared?
- Does the equal-index explanation avoid implying a queue-family ownership transfer?

## Conversion Notes for Final Wiki Rewrite

- Keep the shader section short because shaders only create observable work.
- Carry the behavior-leaf axis and copy the failure mapping table unchanged.
- Preserve separate registration trees for `synchronization.smoke` and `synchronization2.smoke`.
- Keep source navigation in the appendix.
