## Overview

The `synchronization2` test category checks Vulkan synchronization behavior through `VK_KHR_synchronization2` and its Vulkan 1.3 core APIs, including `VkDependencyInfo`, `VkSubmitInfo2`, and the more granular stage/access model. Its implementation is shared with `synchronization`, but this page covers the `SynchronizationType::SYNCHRONIZATION2` registration and mustpass scope.

## Background Knowledge

- **Synchronization scopes:** a synchronization2 barrier names execution and memory scopes separately. The stage/access pair identifies which earlier operations are made available and which later operations can observe them; `NONE` is an empty scope rather than a substitute for the later consumer operation.
- **Queue-family ownership transfer:** an exclusive resource released by one queue family must be acquired by another before the consumer uses it. Synchronization2 operation pages combine this ownership transfer with `VkDependencyInfo` and semaphore submission structures.

## Category Structure

```text
synchronization2
├── smoke
├── timeline_semaphore
├── none_stage
├── internally_synchronized_queues
├── layout_transition
├── basic
├── op
├── cross_instance
├── signal_order
└── implicit
```

`basic` and `op` contain intermediate nodes in the registered hierarchy. The dispatcher `vktSynchronizationTests.cpp` is registration-only; implementation-bearing pages are shared with `synchronization` because the source selects behavior through `SynchronizationType`.

## How the Families Fit Together

The category uses the synchronization2 API model to exercise both shared synchronization concepts and sync2-specific semantics:

- Shared primitive and operation families compare legacy and synchronization2 paths while keeping the underlying resource and verification logic aligned.
- `none_stage` isolates `VK_PIPELINE_STAGE_2_NONE_KHR` and `VK_ACCESS_2_NONE_KHR` behavior across image layouts and aspects.
- `layout_transition` checks synchronization2 image-layout transitions, including the intentional `UNDEFINED`-to-`UNDEFINED` dependency and cross-queue multisample reads.
- `internally_synchronized_queues` checks the extension's internally synchronized queue behavior and has no legacy counterpart.
- Sync2 operation variants use more granular `COPY`, `BLIT`, `RESOLVE`, and `CLEAR` stage values and include maintenance8/maintenance9 coverage where registered.

The legacy gateway documents the parallel `synchronization` category and its legacy-only families; shared implementation pages explain both API paths without duplicating source documentation.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `smoke` | [`SmokeTests.md`](../testfiles/synchronization/SmokeTests.md) | Basic barrier and primitive smoke checks and API routing. |
| `basic.binary_semaphore`, `basic.timeline_semaphore` | [`BasicSemaphore.md`](../testfiles/synchronization/BasicSemaphore.md) | Synchronization2 semaphore sequencing and host/queue variants. |
| `basic.event` | [`BasicEvent.md`](../testfiles/synchronization/BasicEvent.md) | Event state transitions, `NONE` forms, and device-only variants. |
| `op.single_queue` | [`OperationSingleQueue.md`](../testfiles/synchronization/OperationSingleQueue.md) | Synchronization2 operation/resource dependency checks within one queue. |
| `op.multi_queue` | [`OperationMultiQueue.md`](../testfiles/synchronization/OperationMultiQueue.md) | Cross-queue visibility, ownership transfer, and maintenance variants. |
| `cross_instance` | [`CrossInstanceSharing.md`](../testfiles/synchronization/CrossInstanceSharing.md) | External resource/semaphore sharing through sync2 submission/barrier APIs. |
| `signal_order` | [`SignalOrder.md`](../testfiles/synchronization/SignalOrder.md) | Synchronization2 binary and timeline signal-order guarantees. |
| `timeline_semaphore` | [`TimelineSemaphore.md`](../testfiles/synchronization/TimelineSemaphore.md) | Synchronization2 timeline semaphore behavior outside the basic matrix. |
| `none_stage` | [`NoneStageTests.md`](../testfiles/synchronization/NoneStageTests.md) | `NONE` stage/access scopes and image-layout matrix. |
| `layout_transition` | [`ImageLayoutTransition.md`](../testfiles/synchronization/ImageLayoutTransition.md) | Synchronization2 image layout transitions and multisample paths. |
| `internally_synchronized_queues` | [`InternallySynchronized.md`](../testfiles/synchronization/InternallySynchronized.md) | Internally synchronized queue behavior. |
| `implicit` | [`ImplicitTests.md`](../testfiles/synchronization/ImplicitTests.md) | Synchronization2 implicit ordering and visibility behavior. |

The source dispatcher page `vktSynchronizationTests.md` is retained as an obsolete navigation aid, not as an implementation Level-3 page.

## Category Notes

The synchronization2 category has no `basic.fence`, `win32_keyed_mutex`, `global_priority_transition`, or `internally_synchronized_objects` family. Those are legacy-only families. Shared pages must preserve exact category-qualified paths when one source file serves both categories.
