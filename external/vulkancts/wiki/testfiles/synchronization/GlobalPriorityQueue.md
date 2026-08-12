# Global Priority Queue Tests

## Overview

**Core question:** Do Vulkan queues configured with global priorities transfer resource ownership correctly, and do higher-priority submissions complete correctly alongside lower-priority work?

This page covers `synchronization.global_priority_transition`, implemented by [`vktGlobalPriorityQueueTests.cpp`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L2281). It is **LEGACY-only**, excluded from Vulkan SC builds, and is not registered under `synchronization2`; the parent registration is in [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L134-L143).

There are two related behaviors:

- **Queue transitions:** a producer writes an image on one queue family, releases ownership, and a consumer acquires and validates it on another family.
- **Preemption workloads:** a large lower-priority workload and a small higher-priority workload are submitted in sequence; both outputs must be correct. The test cannot prove that physical preemption occurred.

## Registration hierarchy

```text
synchronization.global_priority_transition
├── low
├── medium
├── high
├── realtime
└── preemption
```

The factory is [`createGlobalPriorityQueueTests()`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L2281). Each transition priority expands to `no_sync` and `semaphore`; each sync group expands to `no_modifiers`, `sparse`, and `protected`; each modifier contains four leaves:

```text
from_graphics_to_compute
from_compute_to_graphics
from_compute_to_transfer
from_transfer_to_compute
```

Identical queue types are skipped, as are graphics↔transfer combinations. Transition cases request the same priority on both queue families. The default mustpass list selects 24 transition leaves under each priority and 300 preemption leaves, for **396 leaves total**; see [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt#L31336).

Preemption leaves use `<queueA>_<priorityA>_to_<queueB>_<priorityB>[_double_preemption]`. Queue types are `graphics`, `compute`, `exclusive-compute`, `transfer`, and `exclusive-transfer`. Only cases with `priorityA < priorityB` are generated. The optional suffix submits the small workload twice.

## Queue-transition behavior

A transition case is configured by `GPQCase` and its `TestConfig`. The image dimensions alternate between 34×25 and 25×34; the implementation selects a suitable R-channel format from `R32_SINT`, `R32_UINT`, `R8_SINT`, and `R8_UINT`.

The producer writes the expected value **113**. A pipeline barrier releases the image from the source family; the consumer acquires it on the destination family. `no_sync` submits without a semaphore, while `semaphore` signals after the producer and waits before the consumer.

For non-protected cases, the consumer shader reads pixel (0, 0) and writes `1` when it sees 113, otherwise `0`; the host checks that result buffer. For protected cases, a mismatch enters a deliberate loop and the host detects failure with a ten-second fence timeout. The submission and timeout logic is in [`submitCommands()`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L321-L373).

### Transition dimensions

| Dimension | Values | Effect |
|---|---|---|
| Priority | `low`, `medium`, `high`, `realtime` | Same requested priority for both queues |
| Synchronization | `no_sync`, `semaphore` | Controls explicit semaphore ordering |
| Modifier | `no_modifiers`, `sparse`, `protected` | Adds queue and image requirements |
| Direction | Four listed queue directions | Exercises supported ownership-transfer pairs |
| Image extent | 34×25 or 25×34 | Alternates per generated case |

## Preemption behavior

`PreemptionCase` creates two devices and queues, then prepares a large 512×512 workload for queue A and a small 8×8 workload for higher-priority queue B. It submits A first, submits B, waits for B, optionally submits B again for `_double_preemption`, and finally waits for A.

Graphics output is a gradient checked with `tcu::floatThresholdCompare`. Compute output is an increasing sequence beginning at 0. Transfer output is an increasing sequence beginning at the transfer offset, 1000. A pass means both submissions completed and their results are correct. Because scheduling is implementation-dependent, completion alone does not establish that queue B actually preempted queue A.

## Support requirements

Transition cases require `VK_KHR_get_physical_device_properties2`, `VK_EXT_global_priority`, `VK_EXT_global_priority_query`, suitable format support, and two distinct queue families with the requested priority and queue flags. `sparse` requires sparse binding, sparse buffer residency, and sparse image-2D residency. `protected` requires `protectedMemory`.

Preemption performs its own support checks, including the global-priority functionality needed by its queue/device setup. If creating a requested-priority device returns `VK_ERROR_NOT_PERMITTED_KHR` or `VK_ERROR_INITIALIZATION_FAILED`, the preemption case reports `NotSupportedError`, since denying the requested priority is valid behavior.

## What failures suggest

| Failure pattern | Likely area to investigate |
|---|---|
| Only ownership-transition leaves fail | Queue-family ownership barriers, layout transitions, or inter-queue ordering |
| `semaphore` differs from `no_sync` | Semaphore signal/wait handling or stage-mask interpretation |
| Only `sparse` leaves fail | Sparse feature or queue support |
| Only `protected` leaves hang or time out | Protected queue/memory submission or protected access handling |
| Consumer result is not 1 | Producer write, ownership transfer, acquire visibility, or image read |
| Preemption output is wrong | Queue submission ordering or workload synchronization |
| Priority request is not permitted | Valid implementation policy; expect a quality warning |

## Source map

| Topic | Source |
|---|---|
| Transition configuration, support, and validation | [`vktGlobalPriorityQueueTests.cpp`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L61-L555) |
| Transition shader generation | [`vktGlobalPriorityQueueTests.cpp`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L557-L663) |
| Preemption case and support | [`vktGlobalPriorityQueueTests.cpp`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L1430-L1670) |
| Preemption execution and result checks | [`vktGlobalPriorityQueueTests.cpp`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L2056-L2277) |
| Registration loops | [`vktGlobalPriorityQueueTests.cpp`](../../../modules/vulkan/synchronization/vktGlobalPriorityQueueTests.cpp#L2281-L2420) |
| LEGACY-only parent registration | [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L114-L159) |
| Default mustpass entries | [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt#L31336) |

## Scope note

The former page is preserved as [`vktGlobalPriorityQueueTests.old.md`](vktGlobalPriorityQueueTests.old.md). This rewritten page is the maintained explanation; the `_brief.md` companion records the source-audit mental model, registration counts, and conclusions.
