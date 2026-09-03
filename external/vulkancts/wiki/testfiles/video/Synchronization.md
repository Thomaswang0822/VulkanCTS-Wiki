## Overview

**Core question:** Do Vulkan's basic synchronization primitives (fences, events, binary semaphores, and timeline semaphores) signal, wait, and report state correctly on queues whose only guaranteed capability is video coding?

- This page covers the two video-registered synchronization families, `video.synchronization` and `video.synchronization2`, and their 273 mustpass cases: 161 legacy cases and 112 `VK_KHR_synchronization2` cases, 23 and 16 per codec operation respectively ([`video.txt`](../../../mustpass/main/vk-default/video.txt#L9029-L9301)).
- The video dispatcher registers the two families with one child per codec operation, but the test construction lives in the shared synchronization builders: with a nonzero codec operation, the shared builder attaches only the `basic` family ([registration](../../../modules/vulkan/video/vktVideoTests.cpp#L50-L90), [construction](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L160)).
- The video dimension selects the queue, not the workload. Every case runs on a purpose-built device whose queue family supports the selected codec operation, and the submitted command buffers are empty or contain only event commands. No video session, bitstream, or picture is created ([case example](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L84-L142)).
- Read this page for what the video registration changes: device, queue family, extensions, and the pruned case set. The primitive mechanics and the plain-device case sets are documented by the synchronization category pages, such as [BasicSemaphore](../synchronization/BasicSemaphore.md) and [BasicEvent](../synchronization/BasicEvent.md).

## Background Knowledge

- A queue family advertises video coding through its queue flags, `VK_QUEUE_VIDEO_DECODE_BIT_KHR` or `VK_QUEUE_VIDEO_ENCODE_BIT_KHR`, and reports the supported codec operations in `VkQueueFamilyVideoPropertiesKHR::videoCodecOperations`. A family may expose a video capability without any graphics, compute, or transfer capability, which is why primitive behavior on such queues needs dedicated coverage ([`VkQueueFamilyVideoPropertiesKHR`](../../../../vulkan-docs/src/chapters/devsandqueues.adoc#L1649-L1668)).
- Vulkan has two submission paths for these primitives: the legacy path built on `vkQueueSubmit` with `VkSubmitInfo`, and the `VK_KHR_synchronization2` path built on `vkQueueSubmit2` with `VkSubmitInfo2` and `VkDependencyInfo`. The CTS `SynchronizationWrapper` helper records the same case shape through either path. The synchronization category's [BasicSemaphore](../synchronization/BasicSemaphore.md), [BasicEvent](../synchronization/BasicEvent.md), and [BasicFence](../synchronization/BasicFence.md) pages own the primitive semantics.

## Registration Hierarchy

```text
video.synchronization
├── encode_h264
├── encode_h265
├── encode_av1
├── decode_h264
├── decode_h265
├── decode_av1
└── decode_vp9

video.synchronization2
├── encode_h264
├── encode_h265
├── encode_av1
├── decode_h264
├── decode_h265
├── decode_av1
└── decode_vp9
```

The dispatcher creates each child group with the codec operation's name and passes the corresponding `VkVideoCodecOperationFlagBitsKHR` value into the shared factory, `createSynchronizationTests` for the legacy family and `createSynchronization2Tests` for the synchronization2 family ([registration](../../../modules/vulkan/video/vktVideoTests.cpp#L50-L90)).

Inside each codec child, the shared builder attaches a single `basic` intermediate node: the other shared families, such as the operation and smoke families, are guarded by `videoCodecOperation == 0` and never appear under `video` ([guard](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L122-L157)). Below `basic`, the primitive families `event`, `fence`, `binary_semaphore`, and `timeline_semaphore` hold the leaves listed in the parameter tables.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|---|---|---|---|
| Codec operation | `encode_h264`, `encode_h265`, `encode_av1`, `decode_h264`, `decode_h265`, `decode_av1`, `decode_vp9` | Selects the purpose-built device: encode operations take a queue family with the encode flag, decode operations one with the decode flag, and the extension list grows accordingly. The assertions are identical across codecs. | [registration](../../../modules/vulkan/video/vktVideoTests.cpp#L53-L87), [queue flags](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L688-L701) |
| Synchronization API family | `synchronization`, `synchronization2` | Selects the legacy or `VK_KHR_synchronization2` submission path through the shared wrapper, and with it the available case set: `fence` exists only in legacy, the `none`-stage and device-only event cases only in synchronization2. | [createBasicTests](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L53-L72) |
| Primitive family | `event`, `fence`, `binary_semaphore`, `timeline_semaphore` | The mechanism under test; the primary behavioral axis of this page. | [family assembly](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L58-L69) |
| Case topology | `one_queue`, `multi_queue`, `chain`, `_typed` creation, host or device set-reset, wait-for-any or wait-for-all, `empty_submit`, `none`-stage, `_device_only` events | The submission and wait shape within a primitive family; each leaf changes how the primitive is exercised, not what is verified. | [semaphore leaves](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L933-L1007), [event leaves](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L527-L618), [fence leaves](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L344-L367) |

## Behavior Parameters

The primary behavioral axis is the primitive family below `basic`. Each family exercises one synchronization mechanism on the video-capable queue; the codec and API-family dimensions change the device and the recording path around it.

### `event` — device and host event state transitions

The property under test is that an event can be set, waited on, and reset in submissions to the video-capable queue, and that `vkGetEventStatus` reports the result. The legacy family records a set and a wait in separate command buffers submitted in order, plus a host-side set and reset with status checks between them; the synchronization2 family adds the `none`-stage forms and the `VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR` variants ([legacy and sync2 leaves](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L527-L618)). The host variant checks the event state machine without a queue submission.

### `fence` — fence lifecycle around empty submissions (legacy only)

The property under test is the full fence lifecycle on the video-capable queue: created unsignaled, a short wait times out, a submission with an empty command buffer signals it, a wait succeeds, and a reset returns it to unsignaled. The six leaves vary the number of fences, the `waitAll` setting, presignaled creation, and a submission with no command buffers at all ([case body](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L54-L113), [registration](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L344-L367)). The family exists only in the legacy branch because `createBasicTests` attaches it only for the legacy type.

### `binary_semaphore` — signal and wait ordering across submissions

The property under test is that a binary semaphore correctly orders two submissions on the video-capable queue: the first signals it and the second waits on it. The leaves vary the topology: a single queue with one or two submits, a `_typed` creation through `VkSemaphoreTypeCreateInfo`, two queues from codec-supporting families, and a chain of 32768 submissions, each waiting on the previous semaphore and signaling the next; the synchronization2 family adds `none_wait_submit`, which waits at the `VK_PIPELINE_STAGE_2_NONE` stage ([one-queue case](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L84-L142), [chain case](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L219-L287), [registration](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L933-L966)).

### `timeline_semaphore` — value-ordered submissions and host waits

The property under test is that a timeline semaphore orders submissions by payload value and supports host-side signal and wait on the video device. The shared leaves are a single-queue signal and wait, a cross-queue pair, and a chain where submit *i* waits on value *i* and signals value *i + 1* on one semaphore ([timeline chain](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L289-L363)). The legacy family adds host-only leaves: two threads that hand the semaphore back and forth, and waits for any or all of the current or a lesser value ([registration](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L968-L1007)).

## Shader Analysis

The submitted command buffers are empty or contain only event set, wait, and reset commands. No shaders, pipelines, or other generated program artifacts exist in these cases, and shader behavior is not part of the tested property, so no representative walkthrough applies to this page.

## Runtime Execution and Result Checking

- Every video case starts from the support checks: the build must enable video, the run must not be compute-only, and `VK_KHR_video_queue` plus the encode or decode queue extension and the codec-specific extension must be present ([checkSupport](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L600-L648)).
- The case then constructs a `VideoDevice`: it enumerates queue families, keeps those whose `videoCodecOperations` contain the selected codec and whose queue flags match, enables the video extensions, and creates a logical device with one queue from the first matching family. Timeline cases add the timeline-semaphore requirement and synchronization2 cases add the `VK_KHR_synchronization2` requirement to this device ([device creation](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L820-L1110)).
- The queue comes from `getQueueFamilyVideo`: an encode operation maps to the encode family, a decode operation to the decode family ([queue selection](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L1191-L1204)). The multi-queue leaves instead build a separate device with two queues from codec-supporting families and skip the case as not supported when no such pair exists ([queue search](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L556-L615), [support gate](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L917-L929)).
- Two synchronization2 leaves do not use the video device at all: `none_wait_submit` and `none_set_reset` run on the context device and its universal queue, although their support checks still require the codec operation ([none-stage event case](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L179-L245)).
- The chain leaves submit 32768 times (1024 on Vulkan SC) and touch the watchdog every quarter of the chain so the run is not mistaken for a hang ([chain loop](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L244-L267)).
- Result checking is based only on return codes and object state: every submit, signal, and wait must return `VK_SUCCESS`, fence and event status must match the expected phase, and waits expected to succeed must not time out. No buffer or image content is compared. The `two_threads` leaf is the one exception: a host wait timeout there produces a quality warning instead of a failure ([threaded case](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L437-L443)).

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| `event` | Event set, wait, or reset behavior, or event status reporting, is broken on the video-capable queue or its device. |
| `fence` | Fence signaling, waiting, or reset is broken for submissions on the video-capable queue. |
| `binary_semaphore` | Binary semaphore signal/wait ordering is broken on the video-capable queue, including long submit chains and cross-queue pairs. |
| `timeline_semaphore` | Timeline semaphore host signal/wait or value-based waits are broken on the video device, or the value-ordered submit chain stalls. |

All four values share one additional cause: the purpose-built video device or its queue cannot be created or used, or a submission returns an error.

### Cause Analysis

#### Primitive failure on the video-capable queue

**Possible failure symptoms:** A wait that is expected to succeed returns `VK_TIMEOUT`, a submit or signal call returns an error code, or a polled fence or event state disagrees with the expected phase, such as a fence reporting unsignaled after a completed submission or an event reporting reset after a recorded set.

**Possible implementation causes:** The implementation may not fully support the synchronization primitive on queue families that only advertise video coding capability, for example when the queue's command processing skips semaphore payload handling or event state updates. A chain failure can also come from exhausting an internal synchronization object limit, since the chain leaves create 32768 semaphores or reuse one timeline semaphore across 32768 payload values. The `two_threads` quality warning indicates host-side timeline waits missed the 50 ms timeout, which can be scheduling noise rather than a defect; a hard failure there points at host signal and wait interaction on the video device.

#### Video device and queue selection failure

**Possible failure symptoms:** The case fails or errors during setup, before any primitive is exercised, or the case reports not supported on a device that the reader expects to support the codec.

**Possible implementation causes:** The device creation path chains the video queue extensions with the timeline or synchronization2 feature structures; an implementation that rejects that combination makes every affected leaf fail at device creation. A queue family that reports the codec operation but a `queueCount` of zero, or queue family properties that change between the enumeration and the device creation, also break the selection. A not-supported result, by contrast, is the documented pruning path and not a failure: it means the physical device does not expose the codec operation, the required extension, or the required feature.

## Case Pruning

### Requirement-based pruning

- The build must enable video support; a build with video disabled throws not supported for every leaf in both families ([build gate](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L604-L610)).
- Compute-only runs and missing `VK_KHR_video_queue`, encode or decode queue, or codec-specific extensions prune the case before execution ([support checks](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L612-L642)).
- Timeline-semaphore leaves require the timeline semaphore feature, and all synchronization2 leaves require `VK_KHR_synchronization2`, both on the context and folded into the video device creation ([case support](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L895-L905)).
- Event leaves are pruned when the portability subset disables events ([portability gate](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L505-L509)).
- The multi-queue leaves are pruned when no two usable queues from codec-supporting families exist ([multi-queue gate](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L917-L929)).

### Design-based pruning

- The video registration omits the compute-queue `_cq` forms of every event leaf: a video case already selects its queue through the codec operation, so a second queue-selection variant is meaningless ([skip](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L534-L538)).
- The video registration omits the plain secondary-command-buffer event leaves, with the design comment that secondary command buffers do not apply to video queues; the synchronization2 device-only secondary leaf remains registered ([guard](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L557-L563)).
- The shared builder attaches only the `basic` family for a video codec operation; the operation, smoke, signal-order, and other shared families are plain-category coverage ([guard](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L122-L157)).
- The fence family is legacy-only by construction, and the host-side timeline leaves (`two_threads` and the four wait-for leaves) are not repeated for synchronization2 ([family assembly](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L58-L69), [skip comment](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L987-L1004)).

## Key Takeaways

- The video-registered synchronization cases never submit video work: they validate the basic primitives on a queue whose family supports a codec operation, with empty or event-only command buffers.
- The seven codec children are device and queue selectors (encode versus decode family, plus a growing extension list), not behavioral variants; the assertions are identical across codecs.
- The case set is the plain `basic` family pruned for video: no `_cq` forms, no plain secondary-command-buffer event leaves, no non-basic families, fence only in legacy, and `none`-stage and device-only forms only in synchronization2.
- `none_wait_submit` and `none_set_reset` are the two leaves that run on the context device rather than the video device.
- A failure points at primitive handling on video-capable queues or at the video device creation path, not at codec correctness; see `## Failure Meaning` for the mapping.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|---|---|---|
| Video registration of both families | [video dispatcher](../../../modules/vulkan/video/vktVideoTests.cpp#L50-L90) | Creates the seven codec children per family and passes the codec operation to the shared factories. |
| Shared construction with codec guard | [createTestsInternal](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L160) | Attaches only the `basic` family when a codec operation is given. |
| Basic family assembly | [createBasicTests](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L53-L72) | Selects event, fence, and semaphore builders per API family. |
| Event case set | [createBasicEventTests and createSynchronization2BasicEventTests](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L527-L618) | Registers the event leaves and the video-specific skips. |
| Fence case set | [createBasicFenceTests](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L344-L367) | Registers the six legacy fence leaves. |
| Semaphore case set | [createBasicBinarySemaphoreTests and createBasicTimelineSemaphoreTests](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L933-L1007) | Registers the binary and timeline semaphore leaves per API family. |
| Video device support and flags | [VideoDevice checkSupport and getQueueFlags](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L600-L701) | Defines the extension gates and the encode or decode queue flag selection. |
| Video device creation | [createDeviceSupportingQueue](../../../modules/vulkan/vktCustomInstancesDevices.cpp#L820-L1110) | Queue family search, extension list, and feature requirements. |
| Queue routing for sync cases | [getSyncDevice and getSyncQueue](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L1145-L1178) | Routes every case to the video device and queue or back to the context device. |
| Default mustpass coverage | [video.txt](../../../mustpass/main/vk-default/video.txt#L9029-L9301) | The 273 video synchronization leaves, 161 legacy and 112 synchronization2. |
