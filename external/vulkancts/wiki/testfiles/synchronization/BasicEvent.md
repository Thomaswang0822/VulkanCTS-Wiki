## Overview

**Core question:** Do Vulkan events change state and release device waits correctly across host calls, command buffers, and queue submissions?

- This page covers the `basic.event` test family in both the `synchronization` and `synchronization2` test categories.
- The tests separate direct state transitions from device set/wait flows. State tests query an ordinary event after host or queue completion; wait tests use fence completion to show that execution passed the event wait.
- The synchronization2 path uses `VkDependencyInfo` event commands and adds `NONE`-stage and device-only event cases.
- Each `_cq` test case repeats its unsuffixed counterpart on a compute queue.

## Background Knowledge

- A `VkEvent` has set and reset states. Host commands change and query an ordinary event immediately. Device event commands execute as part of a command buffer.
- A device set and wait form a split dependency. The set operation establishes the first half; the wait operation joins it to later work. The tests in this family use empty dependency information when they need only execution ordering, not memory visibility for a resource.
- Legacy commands carry stage masks and barrier arrays through `vkCmdSetEvent`, `vkCmdWaitEvents`, and `vkCmdResetEvent`. Synchronization2 uses `vkCmdSetEvent2`, `vkCmdWaitEvents2`, `vkCmdResetEvent2`, and `VkDependencyInfo`.
- `VK_EVENT_CREATE_DEVICE_ONLY_BIT` declares that host event commands will not be used. Such an event cannot be queried, set, or reset by the host, so the device-only cases judge success through queue completion.

## Registration Hierarchy

The legacy default mustpass file registers these direct test case leaves:

```text
synchronization.basic.event
├── host_set_reset
├── host_set_reset_cq
├── device_set_reset
├── device_set_reset_cq
├── single_submit_multi_command_buffer
├── single_submit_multi_command_buffer_cq
├── multi_submit_multi_command_buffer
├── multi_submit_multi_command_buffer_cq
├── multi_secondary_command_buffer
└── multi_secondary_command_buffer_cq
```

The synchronization2 default mustpass file registers a different direct set. It omits host set/reset and adds `NONE`-stage and device-only coverage:

```text
synchronization2.basic.event
├── device_set_reset
├── device_set_reset_cq
├── single_submit_multi_command_buffer
├── single_submit_multi_command_buffer_cq
├── single_submit_multi_command_buffer_device_only
├── single_submit_multi_command_buffer_device_only_cq
├── multi_submit_multi_command_buffer
├── multi_submit_multi_command_buffer_cq
├── multi_submit_multi_command_buffer_device_only
├── multi_submit_multi_command_buffer_device_only_cq
├── multi_secondary_command_buffer
├── multi_secondary_command_buffer_cq
├── multi_secondary_command_buffer_device_only
├── multi_secondary_command_buffer_device_only_cq
├── none_set_reset
└── none_set_reset_cq
```

See the exact entries in the [legacy mustpass file](../../../mustpass/main/vk-default/synchronization.txt#L6-L15) and [synchronization2 mustpass file](../../../mustpass/main/vk-default/synchronization2.txt#L7-L22).

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Synchronization API | `synchronization`, `synchronization2` | Selects legacy event/submit commands or synchronization2 commands and dependency structures | [both registration factories](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L527-L617) |
| Queue selection | no suffix, `_cq` | Uses the universal queue or a compute queue | [queue variant loop](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L534-L564) |
| Event creation | ordinary, `_device_only` | Permits host interaction or restricts the event to device commands | [synchronization2 device-only registration](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L605-L614) |
| Set/wait placement | `single_submit_multi_command_buffer`, `multi_submit_multi_command_buffer`, `multi_secondary_command_buffer` | Places the same set-before-wait relationship across command buffers, submissions, or secondary command buffers | [set/wait implementations](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L247-L495) |

The source can also register event cases for video queues. The default `synchronization.txt` and `synchronization2.txt` mustpass files listed above select only the universal and compute queue forms documented by the trees.

## Behavior Parameters

The primary behavioral axis is the event operation flow. Queue and API choices alter where and how that flow runs, while the following values change the property checked.

### `host state transition`: immediate host control

The legacy-only `host_set_reset` cases create an ordinary event, require its initial state to be reset, set it with `vkSetEvent`, and reset it with `vkResetEvent`. `vkGetEventStatus` must report each new state.

### `device state transition`: queued set and reset

The `device_set_reset` cases record a set command, submit it, wait for the queue, and require `VK_EVENT_SET`. They then record and submit a reset command and require `VK_EVENT_RESET`. The wrapper selects legacy or synchronization2 commands for the category.

### `single-submit set/wait`: two command buffers in one submit

One primary command buffer sets the event and a second waits for it. Both appear in one queue submission in that order. The case passes when its fence signals.

### `multi-submit set/wait`: one command buffer per submit

The source submits the set command buffer first and the wait command buffer second to the same queue. It waits for both submission fences, checking that the event dependency works across the submission boundary.

### `secondary-command-buffer set/wait`: commands inherited into one primary

Two secondary command buffers record the set and wait. A primary command buffer executes both secondaries in order, and the host waits for the primary submission's fence.

### `NONE-stage state transition`: synchronization2 zero-stage scope

The synchronization2-only `none_set_reset` cases set an ordinary event using a dependency whose source stage is `VK_PIPELINE_STAGE_2_NONE`, then reset it with the same `NONE` stage. Host status queries after queue completion must still observe set and reset states. The `NONE` value contributes no stages to that scope; it does not suppress the event state operation.

### `device-only set/wait`: no host event commands

Synchronization2 repeats each set/wait placement with `VK_EVENT_CREATE_DEVICE_ONLY_BIT`. These cases never query or modify the event from the host. Fence completion is the observable result.

## Shader Analysis

These tests create no shaders or pipelines. Their device work consists of event commands, command-buffer execution, and queue submission.

## Runtime Execution and Result Checking

- Host state cases call `vkCreateEvent`, `vkGetEventStatus`, `vkSetEvent`, and `vkResetEvent` directly. Each unexpected status or failed host call returns a test failure.
- Device state cases submit one command buffer for the set and another for the reset. The host waits for queue idle before each status query, so the query occurs after the relevant device operation completes.
- Set/wait cases create no data buffer whose contents need validation. They record a set before a wait, submit the work, and wait on one or two fences with an infinite CTS timeout. A non-successful fence wait reports that the queue should have finished.
- `SynchronizationWrapper` translates the shared test logic. The legacy implementation extracts stages and barriers from common dependency structures before calling legacy commands; the synchronization2 implementation calls the `*2` event and submit commands directly.
- The compute-queue forms use a command pool from the compute queue family. Secondary cases first check that the selected family supports `vkCmdExecuteCommands`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `host state transition` | Incorrect host event creation, state update, or status reporting |
| `device state transition` | Incorrect device set/reset execution or host-visible status after queue completion |
| `single-submit set/wait` | Incorrect event dependency or command-buffer ordering within one submission |
| `multi-submit set/wait` | Incorrect event dependency or ordering across consecutive submissions to one queue |
| `secondary-command-buffer set/wait` | Incorrect event handling while executing ordered secondary command buffers |
| `NONE-stage state transition` | Incorrect synchronization2 handling of `VK_PIPELINE_STAGE_2_NONE` for event set/reset |
| `device-only set/wait` | Incorrect device-only event creation or device set/wait handling |

### Cause Analysis

#### Host event state handling

**Possible failure symptoms:** event creation or a host set/reset call fails, or `vkGetEventStatus` reports a state other than the expected initial, set, or reset state.

**Possible implementation causes:** the implementation may mishandle event object initialization, immediate host state updates, or status reporting. The specification requires a successful host update to change the state immediately, so a stale result after the call violates the host event-state contract.

#### Device event state handling

**Possible failure symptoms:** after queue completion, an ordinary event does not report set after the device set or reset after the device reset.

**Possible implementation causes:** command recording or execution may route the wrong event command, apply the state operation incorrectly, or expose stale status after completed queue work. A failure confined to one category can point to the legacy or synchronization2 command path.

#### Set/wait dependency and placement

**Possible failure symptoms:** the completion fence does not return success for one-submit, multi-submit, or secondary-command-buffer work.

**Possible implementation causes:** the implementation may fail to signal the event, fail to release the matching wait, or mishandle submission and command-buffer ordering. A secondary-only failure narrows the problem to event commands executed through `vkCmdExecuteCommands`; a multi-submit-only failure points to preserving the event dependency across consecutive submissions.

#### Synchronization2 special forms

**Possible failure symptoms:** `none_set_reset` reports the wrong state, or a device-only set/wait case fails to complete.

**Possible implementation causes:** the synchronization2 path may treat `VK_PIPELINE_STAGE_2_NONE` as if it removed the event state operation, or may mishandle storage and execution for an event created with `VK_EVENT_CREATE_DEVICE_ONLY_BIT`. Device-only cases do not diagnose host visibility because the specification forbids their use with host event commands.

## Case Pruning

### Requirement-based pruning

- Every synchronization2 case requires `VK_KHR_synchronization2` in this CTS path.
- If `VK_KHR_portability_subset` is enabled and its `events` feature is false, the CTS skips the cases because the implementation does not support events.
- `_cq` cases require an available compute queue.
- Secondary-command-buffer cases require a queue family that supports graphics, compute, or transfer operations. Vulkan SC also requires `secondaryCommandBufferNullOrImagelessFramebuffer`.
- Video variants require the requested video operation and synchronization2 support when they use the synchronization2 path.

### Design-based pruning

- Synchronization2 does not register `host_set_reset`; the legacy family owns the direct host event-state coverage.
- Device-only events appear only in set/wait cases because host status, set, and reset commands are invalid for them.
- Video queue registration omits `_cq` combinations and secondary-command-buffer cases. A video case already selects a video queue, and this test design does not execute the secondary form there.

## Key Takeaways

- State-transition leaves check exact event states. Set/wait leaves check forward progress through fence completion.
- The three set/wait arrangements isolate one submission, consecutive submissions, and secondary command-buffer execution.
- Synchronization2 adds meaningful behavior rather than only renaming commands: it covers a `NONE` stage and device-only events.
- Device-only success cannot be judged with `vkGetEventStatus`; using the completion fence respects the event's host-command restriction.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Host and device state flows | [state test implementations](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L64-L245) | Defines status checks and the synchronization2 `NONE` case |
| Primary command-buffer set/wait flows | [single and multi-submit cases](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L247-L370) | Defines submission placement and fence checks |
| Secondary-command-buffer flow | [secondary case](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L372-L495) | Defines queue support and ordered secondary execution |
| Support and exact registration | [support checks and factories](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L497-L617) | Defines feature gates and both test-family trees |
| Legacy event adaptation | [legacy wrapper event methods](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L664-L771) | Converts common dependency information to legacy commands |
| Synchronization2 event commands | [synchronization2 wrapper event methods](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L890-L918) | Routes shared flows to synchronization2 commands |
| Vulkan event semantics | [event state and device signaling](../../../../vulkan-docs/src/chapters/synchronization.adoc#L5523-L5810) | Specifies device-only restrictions, status behavior, and set semantics |
| Legacy default mustpass | [event leaves](../../../mustpass/main/vk-default/synchronization.txt#L6-L15) | Confirms the selected legacy paths |
| Synchronization2 default mustpass | [event leaves](../../../mustpass/main/vk-default/synchronization2.txt#L7-L22) | Confirms the selected synchronization2 paths |
