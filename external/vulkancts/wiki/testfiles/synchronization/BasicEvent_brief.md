# Understanding Brief: basic event tests

## One-Sentence Test Purpose

This test checks whether host and device event state changes, device waits, and synchronization2-only event forms behave correctly across command-buffer and submission boundaries.

## Background Knowledge

### Event state and event dependencies

A `VkEvent` has set and reset states. Host commands can change and query an ordinary event immediately. Device commands can set, reset, or wait for an event inside command buffers. A device wait also joins the dependency begun by the corresponding set operation; it is more than a status poll.

Why it matters here:
- The state tests can compare an ordinary event with `VK_EVENT_SET` or `VK_EVENT_RESET` after queue completion.
- The wait tests prove progress by waiting for a fence after the set and wait commands have executed in submission order.

### Legacy and synchronization2 forms

The legacy commands pass stage masks and barrier arrays through `vkCmdSetEvent`, `vkCmdWaitEvents`, and `vkCmdResetEvent`. Synchronization2 uses `vkCmdSetEvent2`, `vkCmdWaitEvents2`, `vkCmdResetEvent2`, and `VkDependencyInfo`. The synchronization2 set operation defines the first half of the dependency from its dependency information; the wait supplies the matching second half.

Why it matters here:
- One source implementation routes the same flows through a synchronization wrapper, so the registered category selects the API form.
- Synchronization2 permits a `NONE` stage in the dedicated set/reset test and adds device-only events that host event commands cannot use.

## One Concrete Example

The `single_submit_multi_command_buffer_device_only` case creates an event with `VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR`. One command buffer records a device set. A second records a device wait. The CTS submits both command buffers together in set-then-wait order and waits for a fence. Completion proves that the wait did not stall and that the device-only event worked without a host query, set, or reset.

## End-to-End Test Flow

```text
1. State-transition cases
[host] create an ordinary event
[host or device] set the event
[host] wait for queued work when the device performed the set
[host] query the event and require VK_EVENT_SET
[host or device] reset the event
[host] wait for queued work when the device performed the reset
[host] query the event and require VK_EVENT_RESET

2. Set/wait ordering cases
[host] create an ordinary or device-only event
[host] record a device set in one command buffer
[host] record a device wait in another command buffer
[host] arrange both commands in one submit, two submits, or two secondary command buffers
[device] execute the set before the wait on one queue
[host] wait for the completion fence or fences
[host] pass if the queue finishes; fail if the fence wait does not return success
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The tests generate no shaders or pipelines. They record event commands into primary or secondary command buffers and build either legacy or synchronization2 submit/dependency structures through `SynchronizationWrapper`.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkEvent` | yes | used by commands | set, reset, or waited on | queried only for ordinary state cases | Object under test |
| Primary command buffers | yes | submitted | executed | no | Carry set/reset commands or execute secondary buffers |
| Secondary command buffers | yes | executed by a primary | execute set and wait | no | Exercise event commands across secondary buffers |
| `VkFence` | yes | attached to submission | signaled at completion | waited on by host | Detects whether set/wait execution completes |

Device-only cases deliberately do not call `vkGetEventStatus`, `vkSetEvent`, or `vkResetEvent`, because the specification forbids those host commands for events created with `VK_EVENT_CREATE_DEVICE_ONLY_BIT`.

## What Is Checked

- `host_set_reset`: initial reset state, set state after `vkSetEvent`, and reset state after `vkResetEvent`.
- `device_set_reset`: set state after a submitted device set, then reset state after a submitted device reset.
- `none_set_reset`: the same state sequence using synchronization2 commands with a `NONE` source/reset stage.
- Set/wait cases: fence completion after the set and wait commands execute in the selected command-buffer/submission arrangement.

## Behavior Parameter Identification

> **Behavior parameter:** `event operation flow` (behavioral group)
>
> **Candidate values:** `host state transition`, `device state transition`, `single-submit set/wait`, `multi-submit set/wait`, `secondary-command-buffer set/wait`, `NONE-stage state transition`, `device-only set/wait`

## What Failure Means

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

## Important Variations and Special Cases

- Every normal case has a `_cq` form that selects the compute queue instead of the universal queue.
- The legacy test family includes host state transitions. The synchronization2 test family omits them and adds `none_set_reset` plus device-only forms of all three set/wait arrangements.
- Video registrations reuse the implementation on a video queue, but exclude compute-queue forms and secondary-command-buffer forms. These paths are outside the two default mustpass trees covered by this page.
- The portability subset can report that events are unsupported. Vulkan SC also gates secondary-command-buffer cases on `secondaryCommandBufferNullOrImagelessFramebuffer`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Configuration and host/device state tests | [event configuration and state flows](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L46-L245) | Defines ordinary status checks and the synchronization2 `NONE` case |
| Set/wait arrangements | [single, multi-submit, and secondary flows](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L247-L495) | Defines ordering and completion checks |
| Support and registration | [support gates and both factories](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp#L497-L617) | Defines exact legacy and synchronization2 leaves |
| API routing | [legacy and synchronization2 event wrappers](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L664-L771) | Converts common dependency data to legacy event commands |
| Synchronization2 routing | [synchronization2 event wrapper](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L890-L918) | Calls the synchronization2 event commands |
| Event specification | [event creation, state, and signaling rules](../../../../vulkan-docs/src/chapters/synchronization.adoc#L5523-L5810) | Grounds host visibility, device-only restrictions, and synchronization2 set semantics |

## Questions / Risk Points for User Audit

- Does the behavioral grouping make the difference between state checking and completion checking clear?
- Is it clear that the device-only cases avoid host event commands rather than checking host-visible state?
- Does the page give enough weight to command-buffer/submission placement without implying that these tests validate memory contents?

## Conversion Notes for Final Wiki Rewrite

Keep event state, paired set/wait dependencies, and the device-only host-command restriction as local prerequisites. Preserve the two exact registration trees and explain API routing in prose. Use the event operation flow as the behavior parameter. Copy the failure mapping table unchanged. No shader walkthrough is needed.
