## Overview

**Core question:** Do the basic fence, semaphore, and equal-index queue-family barrier paths complete with the expected host-visible state or data under the legacy and synchronization2 APIs?

- The `smoke` test family provides short checks for submission completion, cross-queue semaphore dependencies, and buffer or image barriers.
- `synchronization.smoke` and `synchronization2.smoke` share semaphore and barrier test logic. The source selects legacy submission and barrier commands or their synchronization2 counterparts.
- The legacy family also contains `fences`. Fence signaling does not have a separate synchronization2 path, so that leaf is absent from `synchronization2.smoke`.
- Buffer cases compare every copied word. Image cases compare one rendered pixel. Semaphore cases require successful submissions and fence waits, but only log their rendered images.

## Background Knowledge

- A fence lets the host query or wait for completion of submitted queue work. It does not order one queue against another queue.
- A semaphore creates a dependency between queue submissions. A binary semaphore carries signaled or unsignaled state; a timeline semaphore carries a monotonically increasing counter value.
- Buffer and image memory barriers establish execution and memory dependencies within command-buffer work. Queue-family indices describe ownership transfer only when the source and destination indices differ. The barrier leaves on this page use the same value for both indices, including special and arbitrary values, so they do not request ownership transfer.

## Registration Hierarchy

The implementation registers one test family under each test category. Both trees contain the same ten shared leaves; only the legacy tree adds `fences`.

```text
synchronization.smoke
├── fences
├── binary_semaphores
├── timeline_semaphores
├── queue_type_ignore_buffer_ignored
├── queue_type_ignore_buffer_external
├── queue_type_ignore_buffer_foreign
├── queue_type_ignore_buffer_arbitrary
├── queue_type_ignore_image_ignored
├── queue_type_ignore_image_external
├── queue_type_ignore_image_foreign
└── queue_type_ignore_image_arbitrary
```

The synchronization2 test category registers the shared leaves under a separate root:

```text
synchronization2.smoke
├── binary_semaphores
├── timeline_semaphores
├── queue_type_ignore_buffer_ignored
├── queue_type_ignore_buffer_external
├── queue_type_ignore_buffer_foreign
├── queue_type_ignore_buffer_arbitrary
├── queue_type_ignore_image_ignored
├── queue_type_ignore_image_external
├── queue_type_ignore_image_foreign
└── queue_type_ignore_image_arbitrary
```

## Parameter Dimensions and Observed Values

| Dimension | Values | Effect on the test |
|---|---|---|
| Test category | `synchronization`, `synchronization2` | Selects `SynchronizationType::LEGACY` or `SynchronizationType::SYNCHRONIZATION2`. The latter uses synchronization2 submission wrappers and `VkBufferMemoryBarrier2` or `VkImageMemoryBarrier2`. |
| Primitive or resource path | fence, semaphore, buffer barrier, image barrier | Selects the completion state or data that the host checks. |
| Semaphore type | `VK_SEMAPHORE_TYPE_BINARY`, `VK_SEMAPHORE_TYPE_TIMELINE` | Selects semaphore creation and whether submission uses timeline value `1`. |
| Queue-family value | `VK_QUEUE_FAMILY_IGNORED`, `VK_QUEUE_FAMILY_EXTERNAL`, `VK_QUEUE_FAMILY_FOREIGN_EXT`, `0xDEADBEEF` | Supplies the same source and destination queue-family index to each tested barrier. |

Support requirements vary by leaf:

| Leaf or variant | Requirement |
|---|---|
| Semaphore leaves | One graphics queue family exposing at least two queues. The current support check also requires `timelineSemaphore`, including for `binary_semaphores`. |
| `timeline_semaphores` | `VK_KHR_timeline_semaphore`; the custom device enables the timeline semaphore feature. |
| Shared leaves under `synchronization2.smoke` | `VK_KHR_synchronization2`. |
| `*_external` | `VK_KHR_external_memory`. |
| `*_foreign` | `VK_EXT_queue_family_foreign`. |

## Behavior Parameters

The primary behavioral axis is the **behavior leaf**. Each leaf chooses the synchronization mechanism, resource, and host-side evidence that determine the failure diagnosis.

### `fences`

This legacy-only leaf submits rendering with one initially unsignaled fence. It checks initial fence state, several wait forms, timeout on a second unsubmitted fence, and the final signaled state of the submitted fence.

### `binary_semaphores`

Queue 0 renders and signals a binary semaphore. Queue 1 waits on that semaphore before rendering a second image. A fence on each submission must complete.

### `timeline_semaphores`

This leaf follows the same two-queue flow with a timeline semaphore. The first submission signals value `1`; the second waits for value `1`.

### `queue_type_ignore_buffer_*`

Each leaf fills a 64-word buffer with `0xAABBCCDD`, then records a transfer-write-to-host-read barrier. The suffix selects one value for both `srcQueueFamilyIndex` and `dstQueueFamilyIndex`. After execution, every word must contain the fill value.

### `queue_type_ignore_image_*`

Each leaf transitions and clears a 1x1 `VK_FORMAT_R8G8B8A8_UNORM` image, renders blue, transitions it for transfer, and copies it to host-visible memory. Every image barrier uses the suffix-selected value for both queue-family fields. The copied pixel must equal `(0, 0, 1, 1)` with zero threshold.

## Shader Analysis

The shaders are not part of the synchronization property, so no representative shader walkthrough is needed. The fence and semaphore paths use a pass-through vertex shader and a fragment shader that writes red to create observable queue work. The image barrier path uses a full-screen triangle and a fragment shader that writes blue; the host checks that blue pixel after the barrier and copy sequence.

## Runtime Execution and Result Checking

- `fences` creates two unsignaled fences, records a 256x256 draw, and submits it with the first fence. Zero-timeout and two-second waits may return either `VK_SUCCESS` or `VK_TIMEOUT`; the infinite wait must return `VK_SUCCESS`. A one-nanosecond wait on the unsubmitted fence must return `VK_TIMEOUT`, and the submitted fence must then report `VK_SUCCESS`. The rendered image is logged but not compared.
- Each semaphore leaf creates a device with two queues from one graphics queue family and records one draw per queue. The first submission signals the selected semaphore, and the second waits on it. The test waits for a fence after each submission. Both images are invalidated and logged, but their pixels do not determine pass or fail.
- Each buffer leaf fills a host-visible buffer on the device, executes either `vkCmdPipelineBarrier` or `vkCmdPipelineBarrier2`, waits for completion, invalidates the allocation, and compares all 64 words with `0xAABBCCDD`.
- Each image leaf records three barriers around clear, render, and copy operations. It uses legacy barriers for `synchronization.smoke` and synchronization2 barriers for `synchronization2.smoke`. After copying the 1x1 image to a buffer, the host performs an exact floating-point threshold comparison against blue.

## Failure Meaning

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

### Cause Analysis

#### Fence state or completion reporting

**Possible failure symptoms:** A new fence reports a state other than `VK_NOT_READY`, a permitted finite wait returns an unexpected error, the unsubmitted fence does not time out, the infinite wait fails, or the submitted fence does not become signaled.

**Possible implementation causes:** The implementation may mishandle initial fence state, host wait timeout rules, or the association between queue completion and fence signal operations. The failing API result identifies the narrower contract that needs source-level investigation.

#### Semaphore submission or completion

**Possible failure symptoms:** Queue submission fails, or either submission fence fails to complete after the signal/wait sequence.

**Possible implementation causes:** The implementation may mishandle the selected semaphore type, timeline value `1`, submission encoding, or semaphore signal and wait dependencies across the two queues. These leaves do not compare rendered pixels, so a pass does not establish image-content correctness.

#### Equal-index buffer barrier or host visibility

**Possible failure symptoms:** One or more buffer words differ from `0xAABBCCDD`, or command submission fails for a selected equal-index value.

**Possible implementation causes:** The implementation may interpret equal source and destination queue-family indices as an ownership transfer, mishandle a special queue-family value, or fail to make transfer writes available and visible to host reads. The legacy or synchronization2 category path identifies the barrier API involved.

#### Equal-index image barriers, transitions, or copyback

**Possible failure symptoms:** The copied pixel differs from exact blue, or recording or submission fails for the selected queue-family value.

**Possible implementation causes:** The implementation may mishandle equal-index barrier semantics, one of the image layout transitions, transfer/color-attachment dependencies, rendering, or image-to-buffer copyback. The test result alone does not prove which stage failed; the command sequence and failing category path guide further investigation.

## Case Pruning

The source registers every combination shown in the hierarchy. It does not prune queue-family suffixes by category. Runtime support checks report unsupported cases when required extensions or features are unavailable. The only structural omission is `fences` from `synchronization2.smoke` because the fence test has no synchronization2-specific command path.

## Key Takeaways

- The two test categories share ten smoke leaves and differ by API path; only `synchronization.smoke` adds `fences`.
- The strongest data checks are in the barrier leaves: 64 exact buffer words or one exact blue image pixel.
- Semaphore leaves check submission and completion of a signal/wait chain. Their logged images are diagnostic output, not pass/fail references.
- Queue-family barrier leaves keep source and destination indices equal, so their special values must not cause an ownership transfer.

## Source Reference Appendix

- [Semaphore configuration, shader payload, and two-queue device setup](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L73-L220)
- [`testFences()` state and wait checks](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1054-L1151)
- [`testSemaphores()` two-queue signal/wait flow](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1154-L1283)
- [Queue-family value mapping and support checks](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1296-L1355)
- [`ignoreQueueFamilyTypeBuffer()` barrier and word comparison](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1393-L1489)
- [`ignoreQueueFamilyTypeImage()` transitions, rendering, and pixel comparison](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1492-L1709)
- [`synchronization.smoke` and `synchronization2.smoke` registration](../../../modules/vulkan/synchronization/vktSynchronizationSmokeTests.cpp#L1725-L1781)
- [Legacy mustpass entries](../../../mustpass/main/vk-default/synchronization.txt#L60017-L60027)
- [Synchronization2 mustpass entries](../../../mustpass/main/vk-default/synchronization2.txt#L78736-L78745)
- [Vulkan synchronization chapter](../../../../vulkan-docs/src/chapters/synchronization.adoc)
