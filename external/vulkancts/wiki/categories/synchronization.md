## Overview

The `synchronization` test category checks whether legacy Vulkan synchronization primitives and execution-dependency operations make writes available and visible to later reads across host waits, submissions, and queue families. Its implementation is shared with `synchronization2`, but this page covers the `SynchronizationType::LEGACY` registration and mustpass scope.

## Background Knowledge

- **Execution and memory dependencies:** ordering a submission or command is not by itself a complete description of when earlier writes become visible to a later access. The test families combine synchronization primitives, pipeline barriers, and queue-family ownership transfers to exercise both ordering and visibility.
- **Queue-family ownership transfer:** an exclusive resource released by one queue family must be acquired by another before the consumer uses it. The operation pages use this concept to distinguish queue-family transfer behavior from the shared resource contents being checked.

## Category Structure

```text
synchronization
├── smoke
├── timeline_semaphore
├── internally_synchronized_objects
├── win32_keyed_mutex
├── global_priority_transition
├── basic
├── op
├── cross_instance
├── signal_order
└── implicit
```

`basic` and `op` contain intermediate nodes in the registered hierarchy. The dispatcher `vktSynchronizationTests.cpp` is registration-only; the implementation-bearing pages below are shared with `synchronization2` because the source selects behavior through `SynchronizationType`.

## How the Families Fit Together

The category covers the same broad visibility question through different synchronization mechanisms:

- **When** the test uses fences, binary semaphores, timeline semaphores, or events, the primitive changes how completion or device-side ordering is established.
- **When** the test uses `op`, the operation and resource matrix changes which write/read dependency is exercised, including single-queue and multi-queue cases.
- Cross-instance sharing and signal-order cases extend the question to exported handles and semaphore signal sequencing.
- `implicit` and the category-specific families check ordering guarantees or platform/API features that do not fit the basic primitive matrix.

The synchronization2 gateway documents the parallel `VK_KHR_synchronization2` category and its additional families; shared implementation pages explain the relevant legacy and synchronization2 paths together.

## Level-3 Pages Navigation

| Registered test family or area | Level-3 page | What to read there |
|---|---|---|
| `smoke` | [`SmokeTests.md`](../testfiles/synchronization/SmokeTests.md) | Basic barrier and primitive smoke checks and their API routing. |
| `basic.fence` | [`BasicFence.md`](../testfiles/synchronization/BasicFence.md) | Legacy fence waits, reset behavior, and completion validation. |
| `basic.binary_semaphore`, `basic.timeline_semaphore` | [`BasicSemaphore.md`](../testfiles/synchronization/BasicSemaphore.md) | Semaphore sequencing, host operations, and queue variants. |
| `basic.event` | [`BasicEvent.md`](../testfiles/synchronization/BasicEvent.md) | Host/device event state transitions and waits. |
| `op.single_queue` | [`OperationSingleQueue.md`](../testfiles/synchronization/OperationSingleQueue.md) | Operation/resource dependency checks within one queue. |
| `op.multi_queue` | [`OperationMultiQueue.md`](../testfiles/synchronization/OperationMultiQueue.md) | Cross-queue visibility and ownership-transfer cases. |
| `cross_instance` | [`CrossInstanceSharing.md`](../testfiles/synchronization/CrossInstanceSharing.md) | External resource/semaphore sharing between instances. |
| `signal_order` | [`SignalOrder.md`](../testfiles/synchronization/SignalOrder.md) | Binary and timeline signal-order guarantees. |
| `timeline_semaphore` | [`TimelineSemaphore.md`](../testfiles/synchronization/TimelineSemaphore.md) | Legacy timeline semaphore behavior outside the basic matrix. |
| `internally_synchronized_objects` | [`InternallySynchronizedObjects.md`](../testfiles/synchronization/InternallySynchronizedObjects.md) | Concurrent use of internally synchronized objects. |
| `win32_keyed_mutex` | [`Win32KeyedMutex.md`](../testfiles/synchronization/Win32KeyedMutex.md) | Legacy Windows keyed-mutex interoperation. |
| `global_priority_transition` | [`GlobalPriorityQueue.md`](../testfiles/synchronization/GlobalPriorityQueue.md) | Global-priority queue transition and workload cases. |
| `implicit` | [`ImplicitTests.md`](../testfiles/synchronization/ImplicitTests.md) | Legacy implicit ordering and visibility behavior. |

The source dispatcher page `vktSynchronizationTests.md` is retained as an obsolete navigation aid, not as an implementation Level-3 page.

## Category Notes

The legacy category has no `none_stage`, `layout_transition`, or `internally_synchronized_queues` family. Those are synchronization2-specific families. The shared pages must preserve exact category-qualified paths when a source file serves both categories.
