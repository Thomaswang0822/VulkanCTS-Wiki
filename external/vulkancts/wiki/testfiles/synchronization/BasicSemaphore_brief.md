# Understanding Brief: Basic Semaphore Tests

## One-Sentence Test Purpose

This test checks whether Vulkan binary and timeline semaphores establish the required execution ordering across submits, queues, threads, and host waits through both legacy submission and `VK_KHR_synchronization2` paths.

## Background Knowledge

### Binary and timeline semaphore state

A binary semaphore carries one signal that a later wait consumes. A timeline semaphore carries a monotonically increasing counter: a wait for value `N` completes when the semaphore reaches at least `N`. Queue submissions use semaphore signal and wait operations to order work without making the host poll device progress.

Why it matters here:
- Binary cases test one-shot handoffs and reuse in separate submission rounds.
- Timeline cases can reuse one semaphore for values `1`, `2`, and onward, and can wait for a value that is already reached.

### Execution and memory dependencies

The Vulkan synchronization chapter distinguishes execution dependencies, which order operations, from memory dependencies, which also make writes available and visible to later accesses. These tests submit empty command buffers, so their primary observable is completion of the semaphore dependency and the final fence or event status. The semaphore wait stage still matters: the sync2-only `none_wait_submit` case checks that `VK_PIPELINE_STAGE_NONE_KHR` is accepted for a semaphore wait while a later command sets an event.

## One Concrete Example

Conceptual single-queue timeline sequence:

```text
[host] create a timeline semaphore at value 0
[host] submit A: signal value 1
[host] submit B: wait for value 1
[host] wait for B's fence
[host] accept the case when the fence reaches VK_SUCCESS
```

The implementation records one simultaneous-use command buffer in both submits. Binary cases use the same shape but signal and wait on the binary semaphore without timeline values. The source uses `SynchronizationWrapper` to select `vkQueueSubmit` or `vkQueueSubmit2`.

## End-to-End Test Flow

```text
[host] select semaphore type, submission API, creation path, and optional video queue operation
[host] check required extensions, features, queue availability, and simultaneous-use support
[host] create semaphore(s), command buffer(s), queue(s), and fence(s)
[host] build legacy or sync2 submit descriptions with semaphore wait/signal information
[device] execute empty command buffers in the submitted dependency order
[host] wait for fences, queue idle, or host-side timeline values
[host] inspect fence/event status and return pass or fail
```

Timeline-only host cases use `vk.signalSemaphore` and `vk.waitSemaphores`. The thread case signals value 1, waits in a worker for 1, signals value 2, and waits in the main thread for 2.

## Generated Test Artifacts and Bound Resources

No shaders, generated program text, descriptor sets, or readback buffers drive these cases. The relevant GPU-visible objects are synchronization and submission objects.

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Binary or timeline semaphore | yes | yes, through submit info | signal/wait state changes | queried through completion | Carries the tested dependency |
| Empty command buffer | yes | yes | executes with no payload work | no | Provides an ordered submission |
| Fence | yes | yes, on selected submit | signaled on completion | yes, via `waitForFences` | Final queue-completion check |
| Event (`none_wait_submit` only) | yes | yes, set by command | set by `cmdSetEvent` | yes, via `getEventStatus` | Confirms the post-wait command ran |

## What Is Checked

- One-queue and multi-queue cases require the relevant submitted fences to return `VK_SUCCESS`.
- Chain cases submit the full dependency chain and wait on its final semaphore through a fence.
- `none_wait_submit` requires both fences to complete and the event status to equal `VK_EVENT_SET`.
- Host timeline waits require `vk.waitSemaphores` to return `VK_SUCCESS` for the selected wait mode and value. The helper issues `vk.signalSemaphore` before that wait but does not inspect its return value.
- The thread case reports pass when the main thread's wait for value `2` succeeds; a 50 ms timeout in either wait produces `QUALITY_WARNING`.

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `binary_semaphore`, `timeline_semaphore`

The `SynchronizationType` dimension (`LEGACY`, `SYNCHRONIZATION2`) and the binary creation dimension (`createSemaphore`, `createSemaphoreType`) are cross-cutting API/configuration variants. They do not define separate semaphore behavior families.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `binary_semaphore` | Binary signal/wait submission ordering, binary semaphore creation, queue-to-queue handoff, long-chain handling, or sync2 `NONE` wait-stage behavior failed; host fence/event observation may also be at fault. |
| `timeline_semaphore` | Timeline feature enablement, monotonic value ordering, queue or thread handoff, host `signalSemaphore`/`waitSemaphores` semantics, or long-chain handling failed; host completion observation may also be at fault. |

## Important Variations and Special Cases

- `synchronization.basic.*` uses legacy submission; `synchronization2.basic.*` uses `VK_KHR_synchronization2` and requires that extension.
- `none_wait_submit` exists only in the synchronization2 binary family.
- `two_threads` and the four `wait_for_*` families exist only in the legacy timeline family because the source does not repeat these host-side tests for sync2.
- Binary tests run once with ordinary `createSemaphore` and once with `createSemaphoreType`; timeline tests use typed timeline creation.
- Chain length is `32768` in ordinary builds and `1024` under Vulkan SC.
- Multi-queue cases require two usable queues, possibly from one or two queue families. Video operation variants select a compatible video device and may add timeline/sync2 requirements.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Test configuration and semaphore creation | [TestConfig and createTestSemaphore](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L49-L67) | Defines the behavioral dimensions and typed/untyped creation split. |
| One-queue and none-stage execution | [basicOneQueueCase and noneWaitSubmitTest](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L85-L217) | Shows submit construction and completion checks. |
| Chain behavior | [basicChainCase and basicChainTimelineCase](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L219-L363) | Shows binary object chains and timeline value chains. |
| Feature and queue gates | [support checks](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L895-L929) | Defines extension, feature, simultaneous-use, and queue requirements. |
| Registration | [factory functions](../../../modules/vulkan/synchronization/vktSynchronizationBasicSemaphoreTests.cpp#L933-L1006) | Defines exact family and test-case names. |
| Vulkan synchronization semantics | [Synchronization and Cache Control](../../../../../external/vulkan-docs/src/chapters/synchronization.adoc#L16-L39) | Defines semaphore purpose and execution/memory dependency context. |
| Registered coverage | [legacy mustpass](../../../../../external/vulkancts/mustpass/main/vk-default/synchronization.txt), [sync2 mustpass](../../../../../external/vulkancts/mustpass/main/vk-default/synchronization2.txt), [SC legacy](../../../../../external/vulkancts/mustpass/main/vksc-default/synchronization.txt), [SC sync2](../../../../../external/vulkancts/mustpass/main/vksc-default/synchronization2.txt) | Confirms both categories and Vulkan SC chain coverage. |

## Questions / Risk Points for User Audit

- Does the distinction between execution ordering and memory visibility stay clear given that the command buffers contain no payload work?
- Should video queue variants receive a separate reader-facing subsection, or is the configuration note sufficient?
- Is the legacy-only status of host timeline waits clear without implying that sync2 cannot use those Vulkan functions?

## Conversion Notes for Final Wiki Rewrite

- Keep the final page focused on semaphore state transitions and completion evidence; move helper names to the appendix.
- Use the conceptual one-queue timeline sequence as the opening execution example.
- Retain the test-family axis for failure mapping and describe API type, creation method, queue count, and chain length as behavior-relevant dimensions.
- Copy the failure mapping table into the final page, then write fresh cause analysis grounded in the submit, wait, and status checks.
