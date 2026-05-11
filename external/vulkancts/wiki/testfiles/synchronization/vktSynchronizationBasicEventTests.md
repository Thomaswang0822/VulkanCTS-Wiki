# vktSynchronizationBasicEventTests

## Overview

Basic event tests for Vulkan synchronization. These tests validate the lifecycle and behavior of VkEvent objects, including host-side set/reset, device-side set/reset via command buffers, wait-events synchronization, secondary command buffer usage, and synchronization2-specific features such as VK_PIPELINE_STAGE_NONE_KHR and VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR. The file contributes to both the LEGACY and synchronization2 categories.

## Role of File

| Category | Group Name | Registration Path |
|---|---|---|
| synchronization (LEGACY) | `basic.event` | `synchronization.basic.event` |
| synchronization2 | `basic.event` | `synchronization2.basic.event` |

The file provides two factory functions: `createBasicEventTests` for LEGACY and `createSynchronization2BasicEventTests` for sync2. Both create a group named `event` but contain different test sets reflecting the capabilities of each synchronization model.

## Source Code

- Implementation: [vktSynchronizationBasicEventTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp)
- Header: [vktSynchronizationBasicEventTests.hpp](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.hpp)

## Registration Hierarchy

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

The LEGACY registration path is `synchronization.basic.event`, created by [`createBasicEventTests()`](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp) which adds the `event` group under `synchronization.basic`.

This file also contributes to the `synchronization2` category via [`createSynchronization2BasicEventTests()`](../../../modules/vulkan/synchronization/vktSynchronizationBasicEventTests.cpp), which registers under `synchronization2.basic.event`. The sync2 path has 16 direct children: the same device-set/reset, single/multi submission, and secondary-command-buffer tests as LEGACY (without host_set_reset), plus sync2-only tests for `none_set_reset`, `none_set_reset_cq`, and six `*_device_only` variants.

## Test Families

### host_set_reset — Host set/reset (LEGACY only)

| Test Name | Function | Compute Queue | Description |
|---|---|---|---|
| `host_set_reset` | `hostResetSetEventCase` | No | Create event on host, verify reset, set, verify set, reset, verify reset |
| `host_set_reset_cq` | `hostResetSetEventCase` | Yes | Same test on a compute queue |

### device_set_reset — Device set/reset

| Test Name | Function | LEGACY | sync2 | Compute Queue | Description |
|---|---|---|---|---|---|
| `device_set_reset` | `deviceResetSetEventCase` | Yes | Yes | No | cmdSetEvent + cmdResetEvent on device; verify status after each |
| `device_set_reset_cq` | `deviceResetSetEventCase` | Yes | Yes | Yes | Same on a compute queue |

### single_submit_multi_command_buffer — Single submission

| Test Name | Function | LEGACY | sync2 | Compute Queue | Description |
|---|---|---|---|---|---|
| `single_submit_multi_command_buffer` | `singleSubmissionCase` | Yes | Yes | No | Set and wait on event in two command buffers within one submit |
| `single_submit_multi_command_buffer_cq` | `singleSubmissionCase` | Yes | Yes | Yes | Same on a compute queue |

### multi_submit_multi_command_buffer — Multi submission

| Test Name | Function | LEGACY | sync2 | Compute Queue | Description |
|---|---|---|---|---|---|
| `multi_submit_multi_command_buffer` | `multiSubmissionCase` | Yes | Yes | No | Set event in one submit, wait in a separate submit |
| `multi_submit_multi_command_buffer_cq` | `multiSubmissionCase` | Yes | Yes | Yes | Same on a compute queue |

### multi_secondary_command_buffer — Secondary command buffer

| Test Name | Function | LEGACY | sync2 | Compute Queue | Description |
|---|---|---|---|---|---|
| `multi_secondary_command_buffer` | `secondaryCommandBufferCase` | Yes | Yes | No | Set and wait on event in secondary command buffers executed via primary |
| `multi_secondary_command_buffer_cq` | `secondaryCommandBufferCase` | Yes | Yes | Yes | Same on a compute queue |

### none_set_reset — None pipeline stage (sync2 only)

| Test Name | Function | Compute Queue | Description |
|---|---|---|---|
| `none_set_reset` | `eventSetResetNoneStage` | No | cmdSetEvent with VK_PIPELINE_STAGE_NONE_KHR src stage; cmdResetEvent with VK_PIPELINE_STAGE_NONE_KHR |
| `none_set_reset_cq` | `eventSetResetNoneStage` | Yes | Same on a compute queue |

### single_submit_multi_command_buffer_device_only — Device-only single submission (sync2 only)

| Test Name | Function | Compute Queue | Event Flags | Description |
|---|---|---|---|---|
| `single_submit_multi_command_buffer_device_only` | `singleSubmissionCase` | No | VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR | Single submit with GPU-only event |
| `single_submit_multi_command_buffer_device_only_cq` | `singleSubmissionCase` | Yes | VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR | Same on a compute queue |

### multi_submit_multi_command_buffer_device_only — Device-only multi submission (sync2 only)

| Test Name | Function | Compute Queue | Event Flags | Description |
|---|---|---|---|---|
| `multi_submit_multi_command_buffer_device_only` | `multiSubmissionCase` | No | VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR | Multi submit with GPU-only event |
| `multi_submit_multi_command_buffer_device_only_cq` | `multiSubmissionCase` | Yes | VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR | Same on a compute queue |

### multi_secondary_command_buffer_device_only — Device-only secondary command buffer (sync2 only)

| Test Name | Function | Compute Queue | Event Flags | Description |
|---|---|---|---|---|
| `multi_secondary_command_buffer_device_only` | `secondaryCommandBufferCase` | No | VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR | Secondary command buffer with GPU-only event |
| `multi_secondary_command_buffer_device_only_cq` | `secondaryCommandBufferCase` | Yes | VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR | Same on a compute queue |

## Parameter Dimensions

### TestConfig

| Field | Type | Values | Description |
|---|---|---|---|
| `type` | SynchronizationType | LEGACY, SYNCHRONIZATION2 | Synchronization model; determines cmdSetEvent/cmdWaitEvents API variant |
| `flags` | VkEventCreateFlags | 0, VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR | Event creation flags |
| `videoCodecOperationFlags` | VideoCodecOperationFlags | 0 or codec flags | When non-zero, tests run on a video-capable queue |
| `computeQueue` | bool | false, true | If true, use a compute queue instead of the universal queue |

### Compute Queue Suffix

| computeQueue | Test Name Suffix |
|---|---|
| false | (none) |
| true | `_cq` |

### Video Queue Exclusion

When `videoCodecOperationFlags != 0`, the `_cq` variants and `multi_secondary_command_buffer` tests are omitted because video queues do not support compute operations or secondary command buffer execution in the same way.

## Support / Feature Requirements

| Test | Check Function | Requirement |
|---|---|---|
| All sync2 tests | `checkSupport` | VK_KHR_synchronization2 |
| All tests on portability subset | `checkSupport` | VK_KHR_portability_subset: events must be supported (portabilitySubsetFeatures.events == true) |
| `_cq` tests | `checkSupport` | Compute queue available via `context.getComputeQueue()` |
| `host_set_reset` | `checkSupport` | Basic event support |
| `device_set_reset` | `checkSupport` | Basic event + device command buffer support |
| `single_submit_multi_command_buffer` | `checkSupport` | Basic event support |
| `multi_submit_multi_command_buffer` | `checkSupport` | Basic event support |
| `multi_secondary_command_buffer` | `checkSecondaryBufferSupport` | Secondary command buffer support; on Vulkan SC requires secondaryCommandBufferNullOrImagelessFramebuffer == VK_TRUE |
| `none_set_reset` | `checkSupport` | VK_KHR_synchronization2 + VK_PIPELINE_STAGE_NONE_KHR |
| `*_device_only` | `checkSupport` | VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR (part of VK_KHR_synchronization2) |

## Verification Methods

### hostResetSetEventCase

1. Create an event with flags=0.
2. Verify `getEventStatus` returns VK_EVENT_RESET.
3. Call `setEvent`; verify VK_EVENT_SET.
4. Call `resetEvent`; verify VK_EVENT_RESET.

### deviceResetSetEventCase

1. Create an event.
2. Record and submit a command buffer with `cmdSetEvent`.
3. Wait for queue idle; verify VK_EVENT_SET.
4. Record and submit a command buffer with `cmdResetEvent`.
5. Wait for queue idle; verify VK_EVENT_RESET.

### eventSetResetNoneStage

1. Create an event.
2. Record `cmdSetEvent` with a VkMemoryBarrier2 having srcStageMask=VK_PIPELINE_STAGE_NONE_KHR.
3. Submit and wait for queue idle; verify VK_EVENT_SET.
4. Record `cmdResetEvent` with stageMask=VK_PIPELINE_STAGE_NONE_KHR.
5. Submit and wait for queue idle; verify VK_EVENT_RESET.

### singleSubmissionCase

1. Create two command buffers (SET and WAIT) and an event.
2. SET buffer: record `cmdSetEvent`.
3. WAIT buffer: record `cmdWaitEvents`.
4. Submit both command buffers in a single `queueSubmit` call.
5. Wait on a fence; verify VK_SUCCESS.

### multiSubmissionCase

1. Create two command buffers (SET and WAIT) and an event.
2. SET buffer: record `cmdSetEvent`.
3. WAIT buffer: record `cmdWaitEvents`.
4. Submit SET buffer with fence[SET].
5. Submit WAIT buffer with fence[WAIT].
6. Wait on both fences; verify VK_SUCCESS.

### secondaryCommandBufferCase

1. Create a primary command buffer and two secondary command buffers.
2. Secondary[SET]: record `cmdSetEvent`.
3. Secondary[WAIT]: record `cmdWaitEvents`.
4. Primary: record `cmdExecuteCommands` with both secondary buffers.
5. Submit primary buffer; wait on fence; verify VK_SUCCESS.

## Test Principles

- **Host vs. device**: LEGACY tests include host-side set/reset verification (`host_set_reset`), while sync2 tests focus on device-side operations only, since VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR events cannot be set or reset from the host.
- **Single vs. multi submission**: The `singleSubmissionCase` tests verify that set and wait operations work within a single queue submission (intra-submit synchronization), while `multiSubmissionCase` tests verify cross-submit synchronization.
- **Secondary command buffers**: The `secondaryCommandBufferCase` tests verify that events can be set in one secondary command buffer and waited upon in another, all executed via a single primary command buffer.
- **Compute queue coverage**: Tests are run on both the universal queue and a dedicated compute queue (when available) to ensure event functionality is not limited to graphics queues.
- **None pipeline stage**: The sync2-only `none_set_reset` tests exercise VK_PIPELINE_STAGE_NONE_KHR, which is a synchronization2 concept that allows setting/resetting events without implying any prior execution dependency.
- **Device-only events**: The sync2-only `*_device_only` tests use VK_EVENT_CREATE_DEVICE_ONLY_BIT_KHR to create events that can only be set/reset from the device, verifying that the implementation correctly restricts host access.
- **SynchronizationWrapper abstraction**: All device-side tests use `SynchronizationWrapper` to abstract the difference between `cmdSetEvent`/`cmdWaitEvents` (LEGACY) and `cmdSetEvent2`/`cmdWaitEvents2` (sync2).

## Notes / Uncertainties

- The `host_set_reset` test is LEGACY-only. The sync2 factory function does not include it, likely because the sync2 extension focuses on device-side synchronization and introduces device-only events.
- The `none_set_reset` test hardcodes `SynchronizationType::SYNCHRONIZATION2` internally (line 200), meaning it always uses the sync2 API path regardless of the TestConfig.
- The `deviceResetSetEventCase` test uses `VkMemoryBarrier2` with srcStage=TOP_OF_PIPE and dstStage=BOTTOM_OF_PIPE for the set operation, and `VK_PIPELINE_STAGE_2_TOP_OF_PIPE_BIT_KHR` for the reset operation. This is a minimal dependency specification.
- Video codec operation flags are passed through but affect which tests are generated (compute queue and secondary command buffer tests are omitted for video queues).
- The `secondaryCommandBufferCase` test checks whether the queue supports `VK_QUEUE_COMPUTE_BIT | VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_TRANSFER_BIT` before executing, to avoid VUID violations on queues that cannot execute secondary command buffers.
