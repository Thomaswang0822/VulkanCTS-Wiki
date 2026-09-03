# Understanding Brief: Video-registered basic synchronization (`video.synchronization` and `video.synchronization2`)

## One-Sentence Test Purpose

This test checks whether Vulkan's basic synchronization primitives — fences, events, binary semaphores, and timeline semaphores — complete their signal, wait, and state transitions correctly on queues whose only guaranteed capability is video coding, without submitting any actual decode or encode work.

## Background Knowledge

### Video-coding queue families

A queue family advertises video coding through its queue flags (`VK_QUEUE_VIDEO_DECODE_BIT_KHR` or `VK_QUEUE_VIDEO_ENCODE_BIT_KHR`) and reports the supported codec operations in `VkQueueFamilyVideoPropertiesKHR::videoCodecOperations`. Video commands may only be submitted to a queue from a family that supports the codec operation.

Why it matters here:

- The tests build their own logical device whose queue family supports the selected codec operation, instead of using the context device.
- A video-capable family is not required to expose graphics, compute, or transfer capability. The tests therefore isolate primitive behavior on a queue that may have no other abilities.

### Legacy and synchronization2 submission paths

The legacy path submits with `vkQueueSubmit` and `VkSubmitInfo`, and records event dependencies with `vkCmdSetEvent`/`vkCmdWaitEvents`. The `VK_KHR_synchronization2` path submits with `vkQueueSubmit2` and `VkSubmitInfo2`/`VkDependencyInfo`. The CTS `SynchronizationWrapper` helper selects between the two at runtime.

Why it matters here:

- The two registered families, `video.synchronization` and `video.synchronization2`, select the wrapper mode for the same case shapes.
- The available case set differs per path: the fence cases exist only in the legacy family, while the `none`-stage and device-only event cases exist only in the synchronization2 family.

## One Concrete Example

Reconstructed conceptual flow of `video.synchronization.decode_av1.basic.binary_semaphore.one_queue`:

```text
[host] VideoDevice for decode_av1: enumerate queue families, pick one whose
       queueFlags contain VK_QUEUE_VIDEO_DECODE_BIT_KHR and whose
       videoCodecOperations contain decode_av1, create a logical device with
       VK_KHR_video_queue, VK_KHR_video_decode_queue, and VK_KHR_video_decode_av1,
       and take one queue from that family
[host] create one binary semaphore, one command buffer (recorded empty), one fence
[host] submit #1: the empty command buffer, signals the semaphore at BOTTOM_OF_PIPE
[host] submit #2: waits on the semaphore at TOP_OF_PIPE, same empty command buffer
[host] waitForFences -> pass only when it returns VK_SUCCESS
```

No image, buffer, or bitstream exists. The queue processes two submissions chained only by the semaphore.

## End-to-End Test Flow

```text
[host] checkSupport: build must enable video; not compute-only; require
       VK_KHR_video_queue and the codec-specific extension; timeline or
       synchronization2 feature required when the case family uses them
[host] construct VideoDevice (with REQUIRE_TIMELINE / REQUIRE_SYNC2 device flags
       as needed): new logical device, video-capable queue family, one queue
[host] create the primitive under test (semaphore / event / fence) and an empty
       command buffer per submission
[host] record: nothing, or only event set / wait / reset commands
[host] submit once, twice, or up to 32768 chained times on the video queue
       (multi-queue cases submit on two queues of a separately created device)
[device] no workload runs; the queue only completes submissions and signals
[host] wait (fence wait, semaphore wait, or queue wait idle) and poll statuses
[host] pass when every return code and every observed state matches expectations
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

None in the shader sense: no shaders, no pipelines, no bitstreams. The command buffers are empty or contain only event commands. The case matrix itself is the only generated artifact.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Binary or timeline semaphore | yes | submit infos | signaled/waited by the queue | no | The primitive under test for semaphore cases. |
| Event | yes | command buffers | set/reset/waited on device or set/reset by host | status polled | The primitive under test for event cases. |
| Fence | yes | submit | signaled by the queue | status polled | Completion handle; the primitive under test for fence cases. |
| Empty command buffer(s) | yes | submit infos | no | no | Forces the queue to process real submissions. |
| `VideoDevice` logical device and queue | yes | — | — | — | Isolates a queue family that supports the codec operation. |

## What Is Checked

- The return code of every submit, signal, and wait call; an unexpected code fails the case immediately.
- Host-visible primitive states: fence transitions (unsignaled, timeout on short wait, signaled after submit, unsignaled after reset), event status (`VK_EVENT_SET`/`VK_EVENT_RESET` after device or host set/reset), and timeline semaphore wait results for current, lesser, any, and all values.
- Waits expected to succeed must not time out; the `two_threads` case instead returns a quality warning on timeout.
- There is no output data to compare: pass/fail is entirely return-code and state based.

## Behavior Parameter Identification

> **Behavior parameter:** synchronization primitive family (the `basic` intermediate node)
>
> **Candidate values:** `event`, `fence`, `binary_semaphore`, `timeline_semaphore`

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `event` | Event set, wait, or reset behavior, or event status reporting, is broken on the video-capable queue or its device. |
| `fence` | Fence signaling, waiting, or reset is broken for submissions on the video-capable queue. |
| `binary_semaphore` | Binary semaphore signal/wait ordering is broken on the video-capable queue, including long submit chains and cross-queue pairs. |
| `timeline_semaphore` | Timeline semaphore host signal/wait or value-based waits are broken on the video device, or the value-ordered submit chain stalls. |

All four values share one additional cause: the purpose-built video device or its queue cannot be created or used, or a submission returns an error.

## Important Variations and Special Cases

- **API family axis:** `synchronization2` omits the fence family and the legacy-only host-side timeline cases, and adds the `none`-stage cases (`none_set_reset`, `none_wait_submit`) and device-only event cases (`*_device_only`).
- **Codec operation axis:** the seven codec children change only the device, queue family, and extension list (decode operations use the decode family, encode operations the encode family); the assertions are identical across codecs.
- **Context-device exceptions:** `none_wait_submit` and `none_set_reset` run on the context device and universal queue, not on the `VideoDevice`, though their support checks still require the codec operation to be supported.
- **Chain length:** the chain cases submit 32768 times (1024 on Vulkan SC builds), touching the watchdog every quarter of the chain.
- **Multi-queue cases:** they create a separate device, pick two queues from codec-supporting families (two queues of one family or one queue each from two families), and are skipped as not supported when no such pair exists.
- **`two_threads` timeout:** a host timeline wait timeout produces a quality warning, not a failure.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Video registration of both families | [video dispatcher](../../../modules/vulkan/video/vktVideoTests.cpp#L50-L90) | Creates the seven codec children under `synchronization` and `synchronization2`. |
| Shared builder entry | [createTestsInternal](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L160) | With a nonzero codec operation only the `basic` family is built. |
| Basic family assembly | [createBasicTests](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L53-L72) | Selects event, fence, and semaphore builders per API family. |
| Event cases | [createBasicEventTests and createSynchronization2BasicEventTests](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L527-L618) | Registers the event case set, including the video pruning of `_cq` and secondary forms. |
| Fence cases | [createBasicFenceTests](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L344-L367) | Registers the six fence leaves. |
| Semaphore cases | [createBasicBinarySemaphoreTests and createBasicTimelineSemaphoreTests](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L933-L1007) | Registers the binary and timeline semaphore leaves per API family. |
| VideoDevice construction and support | [VideoDevice](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L600-L701) | checkSupport, queue flags, and the codec-conditioned constructor. |
| Video device creation | [createDeviceSupportingQueue](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L820-L957) | Queue family search, extension list, and feature requirements. |
| Video queue selection | [getSyncDevice and getSyncQueue](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L1145-L1178) | Routes the sync cases to the video device and queue. |

## Questions / Risk Points for User Audit

- Is "no video work is ever submitted" clearly the central insight, so readers do not expect decode or encode coverage here?
- Is the codec-operation axis correctly presented as a device and queue selector rather than a behavior change?
- Are the two context-device exceptions (`none_wait_submit`, `none_set_reset`) visible enough?
- Does the failure mapping read as primitive-first rather than blaming video coding itself?

## Conversion Notes for Final Wiki Page

- Distill the two Background Knowledge topics into page-local prerequisite bullets; the video category has not consolidated shared prerequisites into Level-2 upward links, so keep the page-local bullet style used by sibling video pages.
- Keep the concrete example only as a compact runtime description; the full case matrix belongs in the parameter tables.
- Copy the Failure Cause Mapping table unchanged; write Cause Analysis fresh, separating primitive failures from device and queue-selection failures.
- State the registration split (video dispatcher registers, shared builders implement) once in the Overview and Registration Hierarchy, not in every section.
