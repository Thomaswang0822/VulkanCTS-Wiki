# Understanding Brief: basic fence tests

## One-Sentence Test Purpose

These tests check whether Vulkan fences correctly report, wait for, transition between, and initially enter their signaled and unsignaled states when associated with queue submissions.

## Background Knowledge

### Fence state and host/device dependency

A `VkFence` has two states: signaled and unsignaled. A queue submission can signal its fence after the submission completes; the host can query the state with `vkGetFenceStatus`, wait with `vkWaitForFences`, and make a signaled fence unsignaled again with `vkResetFences`. The Vulkan synchronization chapter describes a fence as a dependency from a queue to the host ([fences](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-fences)).

### Waiting for one or all fences

`vkWaitForFences` uses `waitAll` to select its completion condition. `VK_TRUE` requires every fence in the array to be signaled; `VK_FALSE` requires at least one. A timeout returns `VK_TIMEOUT` when that condition is not met ([vkWaitForFences](../../../../vulkan-docs/src/chapters/synchronization.adoc#vkWaitForFences)). The timeout values in this test are in nanoseconds, although the implementation's timeout accuracy may be coarser than one nanosecond.

## One Concrete Example

The `synchronization.basic.fence.one` test creates one fence without `VK_FENCE_CREATE_SIGNALED_BIT`. It first observes `VK_NOT_READY`, waits with `SHORT_FENCE_WAIT` and expects `VK_TIMEOUT`, then submits an empty command buffer with that fence. After a `LONG_FENCE_WAIT`, it expects `VK_SUCCESS`, observes `VK_SUCCESS` from `vkGetFenceStatus`, resets the fence, and expects `VK_NOT_READY` again. This is a compact create → wait/query → queue signal → wait/query → reset sequence.

## End-to-End Test Flow

```text
[host] select the optional video queue/device configuration
[host] create a device fence and, where needed, a command pool and command buffer
[host] query the initial fence state and perform short waits on unsignaled fences
[host] record an empty command buffer when the case uses one
[host] submit work with a fence, or submit with zero command buffers for empty_submit
[device] execute the queue submission and its fence signal operation
[host] wait with the requested waitAll and timeout values
[host] query or reset fences and compare each Vulkan result with the expected state
[host] return pass or fail from the checked Vulkan results
```

The two-fence cases repeat this flow with a first and second fence. They deliberately create no-fence-signaled, one-fence-signaled, and both-fences-signaled states so that `waitAll=VK_FALSE` and `waitAll=VK_TRUE` can be compared.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

No shader, generated program, or SPIR-V artifact is used. The test records an empty command buffer only to provide queue work for the fence signal operation.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| `VkFence` | yes | no | its state is advanced by queue completion | queried/waited by host | The object under test. |
| Empty `VkCommandBuffer` | yes, in cases that submit one | submitted to queue | no application-visible commands | no | Supplies a repeatable queue submission without another synchronization result. |

`empty_submit` passes `commandBufferCount=0` and `pCommandBuffers=nullptr` to `vkQueueSubmit`; it still supplies a fence and waits for that fence.

## What Is Checked

- A fence created with flags `0` is `VK_NOT_READY`.
- A short wait on an unsignaled fence returns `VK_TIMEOUT`; the state remains unsignaled.
- A fence attached to a completed queue submission becomes waitable and queryable as `VK_SUCCESS`.
- `vkResetFences` returns a signaled fence to `VK_NOT_READY`.
- `VK_FENCE_CREATE_SIGNALED_BIT` makes each newly created fence immediately signaled.
- For two fences, `waitAll=VK_FALSE` succeeds once either fence is signaled, while `waitAll=VK_TRUE` waits for both.
- The successful waits use `LONG_FENCE_WAIT`; the source defines it as `1000000000ull` nanoseconds (1 second), while `SHORT_FENCE_WAIT` is `1000ull` nanoseconds (1 microsecond).

## Behavior Parameter Identification

> **Behavior parameter:** test family
>
> **Candidate values:** `one`, `multi`, `empty_submit`, `multi_waitall_false`, `one_signaled`, `multiple_signaled`

The `FenceConfig::numFences` value (`1` or `10`) specializes the two pre-signaled cases, while `videoCodecOperationFlags` selects an optional video-capable device/queue. Neither changes the fence rule being checked, so the test family is the primary behavioral axis.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `one` | Incorrect fence initial state, queue-to-host signal/wait behavior, status query, or reset behavior. |
| `multi` | Incorrect fence reuse or `waitAll=VK_TRUE` behavior with two submissions; simultaneous-use command-buffer support or setup may also be unavailable. |
| `empty_submit` | Incorrect handling of a zero-command-buffer queue submission with a fence, or fence wait behavior. |
| `multi_waitall_false` | Incorrect any-versus-all wait condition or transition between none, partial, and complete signaling. |
| `one_signaled` | Incorrect handling of `VK_FENCE_CREATE_SIGNALED_BIT` or waiting on an initially signaled fence. |
| `multiple_signaled` | Incorrect creation or all-fence wait behavior for ten initially signaled fences; simultaneous-use support or setup may also be unavailable. |

## Important Variations and Special Cases

- `one_signaled` creates one pre-signaled fence; `multiple_signaled` creates ten and waits for all of them. Both use the same `basicSignaledCase` implementation.
- `multi`, `multi_waitall_false`, and `multiple_signaled` request `VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT`. The support check also rejects Vulkan SC implementations whose `commandBufferSimultaneousUse` property is `VK_FALSE`.
- A nonzero `videoCodecOperationFlags` causes the helpers to use `VideoDevice` and check video support. It changes the device/queue selection, not the fence assertions.
- The implementation registers this test family only in the legacy synchronization path; the synchronization2 test-category registration does not call `createBasicFenceTests`.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Fence constants and `FenceConfig` | [`SHORT_FENCE_WAIT`, `LONG_FENCE_WAIT`, `FenceConfig`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L45-L52) | Defines timeout values and specialization fields. |
| Single-fence lifecycle | [`basicOneFenceCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L54-L113) | Implements initial query, timeout, submit, signal wait, and reset checks. |
| Pre-signaled fences | [`basicSignaledCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L131-L164) | Creates one or ten fences with `VK_FENCE_CREATE_SIGNALED_BIT`. |
| Two-fence reuse | [`basicMultiFenceCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L166-L235) | Reuses the first fence and waits for both fences. |
| Empty submission | [`emptySubmitCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L237-L259) | Submits zero command buffers with a fence. |
| Any/all waits | [`basicMultiFenceWaitAllFalseCase`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L261-L340) | Checks none, partial, and complete signaling for both `waitAll` values. |
| Test registration | [`createBasicFenceTests`](../../../modules/vulkan/synchronization/vktSynchronizationBasicFenceTests.cpp#L344-L368) | Defines the six exact test case leaves. |
| Legacy-only parent registration | [`vktSynchronizationTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L61-L66) | Shows that the fence test family is not added to synchronization2. |
| Mustpass coverage | [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt#L16-L21) | Lists all six legacy `dEQP-VK.synchronization.basic.fence.*` cases. |
| Vulkan fence semantics | [`Fences`](../../../../vulkan-docs/src/chapters/synchronization.adoc#synchronization-fences) | Defines the two states and queue-to-host dependency. |
| Vulkan wait semantics | [`vkWaitForFences`](../../../../vulkan-docs/src/chapters/synchronization.adoc#vkWaitForFences) | Defines `waitAll`, timeout, `VK_SUCCESS`, and `VK_TIMEOUT`. |
| Vulkan initial state | [`VkFenceCreateFlagBits`](../../../../vulkan-docs/src/chapters/synchronization.adoc#VkFenceCreateFlagBits) | Defines `VK_FENCE_CREATE_SIGNALED_BIT`. |

## Questions / Risk Points for User Audit

- Is the distinction between fence state checks and queue completion clear?
- Is the `waitAll` any-versus-all contrast clear enough for the partial-signaling case?
- Should the final page retain the Vulkan SC simultaneous-use prerequisite, or is the source link sufficient?
- Is the empty-submission case explained without implying that it executes application commands?

## Conversion Notes for Final Wiki Rewrite

- Keep `## Background Knowledge` to the two fence concepts above; do not copy the teaching prose verbatim.
- Use the single-fence sequence as the concrete runtime example and explain the two-fence cases as variations.
- Keep `test family` as the primary behavior parameter and copy the failure mapping table directly into the final page.
- Put source and spec links in the appendix, with only the most useful function links inline.
- The page has no shader analysis; state that directly rather than inventing a walkthrough.
