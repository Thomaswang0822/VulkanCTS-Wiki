# Timeline semaphore tests

Source: [`vktSynchronizationTimelineSemaphoreTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp)

## Scope

This source builds the timeline-semaphore suites under both Vulkan synchronization roots:

- `synchronization.timeline_semaphore` uses `SynchronizationType::LEGACY` and the legacy queue-submit path.
- `synchronization2.timeline_semaphore` uses `SynchronizationType::SYNCHRONIZATION2` and the synchronization2 submit/barrier path.

Most test logic is shared. [`SynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp) translates common submit and barrier descriptions to the selected API. The public factories are declared in [`vktSynchronizationTimelineSemaphoreTests.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.hpp).

## Test hierarchy

```text
synchronization.timeline_semaphore
├── device_host
│   ├── <write>_<read>/<resource>
│   └── misc
│       ├── max_difference_value
│       └── initial_value
├── one_to_n/<write>_<read>/<resource>
├── wait_before_signal/<write>_<read>/<resource>
├── wait
│   ├── all_signal_from_device
│   ├── one_signal_from_device
│   ├── all_signal_from_host
│   ├── one_signal_from_host
│   ├── host_wait_before_signal
│   ├── poll_signal_from_device
│   └── poll_signal_from_host
├── sparse_bind                         # not built for Vulkan SC
│   ├── no_sems
│   ├── no_wait_sig
│   ├── wait_no_sig
│   ├── wait_and_sig
│   └── wait_and_sig_2
└── misc/ignore_timeline_semaphore_info
```

```text
synchronization2.timeline_semaphore
├── device_host
│   ├── <write>_<read>/<resource>
│   └── misc/max_difference_value
├── one_to_n/<write>_<read>/<resource>
├── wait_before_signal/<write>_<read>/<resource>
└── wait
    ├── all_signal_from_device
    ├── one_signal_from_device
    ├── all_signal_from_host
    ├── one_signal_from_host
    ├── host_wait_before_signal
    ├── poll_signal_from_device
    └── poll_signal_from_host
```

The legacy-only pieces are `device_host.misc.initial_value`, `sparse_bind`, and `misc.ignore_timeline_semaphore_info`. `sparse_bind` is also excluded when the CTS is built for Vulkan SC.

## Generated operation cases

`device_host`, `one_to_n`, and `wait_before_signal` use the same case-generation scheme. They enumerate 19 writers and 28 readers, then visit the resource descriptions in [`vktSynchronizationOperationTestData.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp). A leaf is added only when both operations support that resource, so the tree is a filtered cross-product rather than every theoretical combination.

The writers cover transfer operations and SSBO/image writes from graphics and compute stages. The readers cover transfer operations; UBO, SSBO, and image reads from graphics and compute stages; indirect draw/dispatch buffers; and vertex input. Names come from the shared operation and resource helpers, producing paths such as:

```text
<root>.timeline_semaphore.device_host.<write>_<read>.<resource>
<root>.timeline_semaphore.one_to_n.<write>_<read>.<resource>
<root>.timeline_semaphore.wait_before_signal.<write>_<read>.<resource>
```

Each family shares pipeline-cache data across its generated leaves to reduce repeated pipeline construction.

## Test behavior

### `device_host`

Builds twelve iterations around one timeline semaphore. Each iteration records a GPU writer followed by a GPU reader. Timeline values order the writer, reader, and host handoff. A host thread waits for each reader value, copies that reader's output into the next writer, and signals the next CPU value. After all submissions complete, the test compares the first input with the final output.

The nested `misc` group adds:

- `max_difference_value`: exercises values constrained by `maxTimelineSemaphoreValueDifference`.
- `initial_value`: checks immediate waits and counter queries for zero and nonzero initial values. This case is registered only in the legacy tree.

### `one_to_n`

Submits one producer and fans its result out through multiple copy/read operations on available queues. A timeline signal gates the downstream work. The test waits for completion and checks every consumer's data, covering the rule that one timeline point can release multiple dependent submissions.

### `wait_before_signal`

Submits dependent queue work before the value it waits for has been signaled. The host later signals the starting timeline point, allowing the queued chain to run. Final data checks show that waits submitted ahead of their matching signal are honored and that the dependency chain completes correctly.

### `wait`

Exercises host wait and counter-query behavior directly:

| Case | Expected behavior |
|---|---|
| `all_signal_from_device` | Wait-all completes after device submissions signal every semaphore. |
| `one_signal_from_device` | Wait-any completes after a device submission signals one semaphore. |
| `all_signal_from_host` | Wait-all completes after host signals every semaphore. |
| `one_signal_from_host` | Wait-any completes after host signals one semaphore. |
| `host_wait_before_signal` | A zero-timeout wait first returns `VK_TIMEOUT`; after the prerequisite signal, the wait succeeds. |
| `poll_signal_from_device` | Counter polling observes a value signaled by queue submission. |
| `poll_signal_from_host` | Counter polling observes a host-signaled value. |

### `sparse_bind` (legacy only)

Combines timeline semaphore waits and signals with `vkQueueBindSparse`. The five leaves cover 0/0, 0/1, 1/0, 1/1, and 2/2 wait/signal semaphore counts. The group is guarded by `#ifndef CTS_USES_VULKANSC`.

### `misc.ignore_timeline_semaphore_info` (legacy only)

Submits binary semaphores with a `VkTimelineSemaphoreSubmitInfo` structure in the `pNext` chain whose value counts do not describe timeline semaphores. Compute work and a copied result confirm that the structure is ignored when no timeline semaphore is present, including avoiding use of irrelevant value arrays.

## Support and API selection

All leaves require timeline semaphore functionality through `VK_KHR_timeline_semaphore` (or its core equivalent as handled by the CTS). Synchronization2-generated leaves additionally require `VK_KHR_synchronization2`. Generated operation cases call each selected operation's support check, which accounts for required shader stages, formats, usages, and other operation-specific capabilities.

The common code uses timeline creation, `vkWaitSemaphores`, `vkSignalSemaphore`, and `vkGetSemaphoreCounterValue`. Queue submissions and command-buffer barriers go through `SynchronizationWrapper`, selecting legacy `vkQueueSubmit`/barriers or synchronization2 submit/barrier structures according to the root. The sparse-bind family intentionally uses the legacy sparse-binding API.

## Pass criteria

A case passes only when its relevant observable results agree with the timeline dependency:

- produced and consumed resource bytes match;
- all fan-out consumers contain the expected data;
- waits return `VK_SUCCESS` or `VK_TIMEOUT` at the intended point;
- queried semaphore counters reach the expected values;
- initial values and the maximum-value-difference property are respected; and
- sparse-bind and ignored-submit-info cases complete without corrupting their verified output.

## Source map

| Area | Source symbol |
|---|---|
| Legacy root | `createTimelineSemaphoreTests()` |
| Synchronization2 root | `createSynchronization2TimelineSemaphoreTests()` |
| Host/device chain | `DeviceHostTestInstance`, `HostCopyThread` |
| Fan-out | `OneToNTestInstance` |
| Pre-signal submission | `WaitBeforeSignalTestInstance` |
| Host waits and polling | `WaitTests` and its test cases |
| Sparse binding | `SparseBindGroup`, `SparseBindInstance` |
| Ignored submit info | `ignoreTimelineSemaphoreSubmitInfoRun()` |
