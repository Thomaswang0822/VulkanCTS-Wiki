## Overview

**Core question:** Do binary and timeline semaphores order the submitted work and host waits correctly across one queue, multiple queues, threads, and both Vulkan submission APIs?

- [vktSynchronizationBasicSemaphoreTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp) implements the `basic.binary_semaphore` and `basic.timeline_semaphore` test families.
- The same factories register under `synchronization.basic` for legacy submission and `synchronization2.basic` for `VK_KHR_synchronization2`.
- The tests use empty command buffers and observe completion through fences, queue idle, event status, or host timeline waits.
- The page covers the exact registered cases, their support gates, and what each failure can establish.

## Background Knowledge

- A binary semaphore carries a single signal that a later queue wait consumes. A timeline semaphore carries a monotonically increasing counter, so a wait for value `N` completes when the counter reaches at least `N`.
- Vulkan separates execution dependencies from memory dependencies. This file tests the ordering and completion contract of semaphore operations; its empty command buffers do not test application payload visibility.
- `vkQueueSubmit` and `vkQueueSubmit2` describe equivalent dependency patterns through different submit structures. The source's `SynchronizationWrapper` selects the path from `SynchronizationType`.

## Registration Hierarchy

```text
synchronization.basic
├── binary_semaphore
└── timeline_semaphore
```

```text
synchronization2.basic
├── binary_semaphore
└── timeline_semaphore
```

The two roots share the same direct semaphore families. Their test case leaves differ by API path:

| Test family | `synchronization.basic` leaves | `synchronization2.basic` leaves |
|---|---|---|
| `binary_semaphore` | `one_queue`, `one_queue_typed`, `multi_queue`, `multi_queue_typed`, `chain` | `one_queue`, `one_queue_typed`, `multi_queue`, `multi_queue_typed`, `none_wait_submit`, `chain` |
| `timeline_semaphore` | `one_queue`, `multi_queue`, `chain`, `two_threads`, `wait_for_any_current_value`, `wait_for_any_lesser_value`, `wait_for_all_current_value`, `wait_for_all_lesser_value` | `one_queue`, `multi_queue`, `chain` |

## Parameter Dimensions and Observed Values

| Dimension | Observed values | Effect on the test |
|---|---|---|
| Test family | `binary_semaphore`, `timeline_semaphore` | Selects one-shot signal/wait behavior or counter-based values. |
| Synchronization type | `LEGACY`, `SYNCHRONIZATION2` | Selects `vkQueueSubmit` or `vkQueueSubmit2` through `SynchronizationWrapper`. |
| Binary creation | `createSemaphore`, `createSemaphoreType` | Runs binary tests through ordinary and typed semaphore creation. The registered suffix is `_typed` for the latter. |
| Queue topology | one queue, two queues | Changes whether the handoff stays on one queue or crosses queue handles and possibly queue families. |
| Timeline values | `1`, `2`, increasing chain values, or wait value `1` | Tests equality, greater-than-or-equal waits, and monotonic progression. |
| Host wait mode | any/all, current/lesser | Uses `VK_SEMAPHORE_WAIT_ANY_BIT` or wait-for-all with signal values `1` or `4` and wait value `1`. |
| Chain length | `32768` default, `1024` Vulkan SC | Controls the long dependency chain stress case. |
| Video operation | `0` or video codec flags | Selects the normal device or a compatible video-capable queue; timeline and sync2 requirements are added when needed. |

## Behavior Parameters

The primary behavioral axis is the **test family**. API path, creation path, queue topology, timeline values, and chain length vary the same semaphore contract rather than defining new families.

### `binary_semaphore`: one-shot queue handoffs

- `one_queue` signals a binary semaphore in one submit and waits on it in a second submit on the same queue.
- `one_queue_typed` repeats that flow after typed creation with `createSemaphoreType`.
- `multi_queue` and `multi_queue_typed` signal on one queue, wait and signal on another, then reverse the queue roles in a second round.
- `chain` creates a new binary semaphore at each link. Each submit waits on the previous link and signals the next, and the final submit waits on the last link.
- `none_wait_submit` is sync2-only. It signals a binary semaphore, waits for it with `VK_PIPELINE_STAGE_NONE_KHR`, sets an event at `VK_PIPELINE_STAGE_TOP_OF_PIPE_BIT`, and checks that the event becomes set.

### `timeline_semaphore`: counter-based queue and host waits

- `one_queue` signals value `1` and waits for value `1` on one queue.
- `multi_queue` uses values `1` and `2` in the first cross-queue round, then values `3` and `4` after swapping roles.
- `chain` reuses one timeline semaphore. Submit `i` waits for value `i` and signals `i + 1`; the final submit waits for the chain length.
- `two_threads` is legacy-only. The worker waits for value `1` and signals `2`; the main thread signals `1` and waits for `2`.
- The four `wait_for_*` cases call `vk.signalSemaphore` and then `vk.waitSemaphores`: `any` sets `VK_SEMAPHORE_WAIT_ANY_BIT`, while `all` uses zero flags; `current` signals `1`, and `lesser` signals `4` before waiting for `1`.

## Shader Analysis

This test file contains no shaders. The command buffers are empty, so shader execution and shader-generated artifacts do not participate in the tested behavior.

## Runtime Execution and Result Checking

- Support checks require `VK_KHR_timeline_semaphore` for timeline cases and `VK_KHR_synchronization2` for sync2 cases. One-queue and multi-queue cases also require simultaneous-use command-buffer support; multi-queue cases require two usable queues.
- The one-queue flow creates one semaphore, one simultaneous-use command buffer, and a fence. The first submit signals at the bottom-of-pipe stage; the second waits at the top-of-pipe stage. The fence must return `VK_SUCCESS`.
- The multi-queue flow creates a custom device with two queues, submits the first handoff, waits on both fences, swaps the signal/wait roles, and waits again.
- Binary and timeline chain flows submit the required dependency links, touch the watchdog every quarter of the chain, submit a final wait with a fence, and wait for that fence.
- `none_wait_submit` waits for queue idle, waits for both fences, and checks `getEventStatus` for `VK_EVENT_SET`.
- Host timeline helpers issue `vk.signalSemaphore`, then check the return value from `vk.waitSemaphores`. The thread case reports pass from the main wait result and treats a timeout in either thread as `QUALITY_WARNING`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `binary_semaphore` | Binary signal/wait submission ordering, binary semaphore creation, queue-to-queue handoff, long-chain handling, or sync2 `NONE` wait-stage behavior failed; host fence/event observation may also be at fault. |
| `timeline_semaphore` | Timeline feature enablement, monotonic value ordering, queue or thread handoff, host `signalSemaphore`/`waitSemaphores` semantics, or long-chain handling failed; host completion observation may also be at fault. |

### Cause Analysis

#### Binary dependency or completion failure

**Possible failure symptoms:** A fence does not reach `VK_SUCCESS`, a submit returns an error, or a binary chain cannot complete. In `none_wait_submit`, the event remains unset after both fences complete.

**Possible implementation causes:** The implementation may mishandle binary semaphore state transitions, a queue-to-queue signal/wait dependency, or the `VK_PIPELINE_STAGE_NONE_KHR` wait-stage description. The source does not identify a bug location; further investigation must compare the failing path with the Vulkan semaphore and synchronization2 requirements.

#### Timeline value or host-wait failure

**Possible failure symptoms:** A queue fence fails to complete, a timeline chain stalls, `vk.waitSemaphores` returns something other than `VK_SUCCESS`, or the two-thread handshake does not finish before its timeout.

**Possible implementation causes:** The implementation may mishandle monotonic timeline values, value-based queue waits, cross-queue propagation, or host signal/wait operations. The observed result alone does not distinguish device, driver, or host-side causes; source-level and API-call investigation is needed.

## Case Pruning

### Requirement-based pruning

- Timeline cases are skipped when `VK_KHR_timeline_semaphore` or the required timeline feature is unavailable.
- Sync2 cases are skipped when `VK_KHR_synchronization2` is unavailable.
- One-queue and multi-queue cases are skipped without simultaneous-use support. Multi-queue cases also require two matching queues.
- Video variants require support for the requested codec operation and compatible queue flags.
- Vulkan SC uses a shorter chain length, `1024`, and also checks the `commandBufferSimultaneousUse` property.

### Design-based pruning

The source registers host timeline waits and the thread handshake only for `LEGACY`; it intentionally does not repeat them under synchronization2. The binary family registers typed and untyped creation variants, while the timeline family always uses typed timeline creation. The sync2-only `none_wait_submit` case exists to exercise the `NONE` wait-stage form.

## Key Takeaways

- Binary tests validate one-shot semaphore handoffs, including a reversed cross-queue round and a long chain.
- Timeline tests validate counter progression, waits satisfied by an equal or greater value, cross-queue reuse, and selected host-side operations.
- The same queue dependency intent runs through legacy and sync2 submit APIs, while registration intentionally differs for host-only timeline cases and the sync2 `NONE` wait-stage case.
- These tests establish semaphore ordering and completion behavior. They do not validate payload visibility because the command buffers contain no payload work.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| `TestConfig`, `createTestSemaphore` | [configuration](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L49-L67) | Defines type, API, creation, and video dimensions. |
| `basicOneQueueCase`, `noneWaitSubmitTest` | [single-queue flows](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L85-L217) | Defines submit order and fence/event checks. |
| `basicChainCase`, `basicChainTimelineCase` | [chain flows](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L219-L363) | Defines binary and timeline chain construction. |
| `basicThreadTimelineCase`, timeline wait helpers | [host timeline flows](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L365-L515) | Defines thread and `waitSemaphores` behavior. |
| `basicMultiQueueCase` | [multi-queue flow](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L633-L892) | Defines custom queue creation, role reversal, and fence checks. |
| `checkSupport`, `checkMultiQueueSupport` | [support gates](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L895-L929) | Defines required extensions, features, and queues. |
| `createBasicBinarySemaphoreTests`, `createBasicTimelineSemaphoreTests` | [registration](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L933-L1006) | Defines exact registered family and test-case names. |
| Vulkan synchronization chapter | [execution and memory dependencies](../../../../../external/vulkan-docs/src/chapters/synchronization.adoc#L16-L39) | Places semaphore ordering in Vulkan's synchronization model. |
| Mustpass definitions | [synchronization](../../../../../external/vulkancts/mustpass/main/vk-default/synchronization.txt), [synchronization2](../../../../../external/vulkancts/mustpass/main/vk-default/synchronization2.txt) | Confirms legacy and sync2 registered coverage. |

