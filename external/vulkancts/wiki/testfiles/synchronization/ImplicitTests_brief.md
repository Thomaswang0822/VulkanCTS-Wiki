# Understanding Brief: implicit synchronization tests

## One-Sentence Test Purpose

These tests check that one queue preserves the ordered semaphore dependencies created by several `VkSubmitInfo` or `VkSubmitInfo2` structures submitted in one call.

## Background Knowledge

### Submission order and resource visibility

A queue submission call receives an ordered list of submit structures. Each structure may wait on semaphores, run command buffers, and signal semaphores. This test builds a complete dependency chain: every wait has a matching signal, every signal has a matching wait, and every read has a paired write. Vulkan still leaves resource visibility to synchronization operations, so the test records a pipeline barrier for the paired write and read. The result isolates ordering between submit structures from an intentionally missing resource barrier. The specification's synchronization overview describes the limited implicit guarantees and the need for explicit resource synchronization ([synchronization.adoc](../../../../vulkan-docs/src/chapters/synchronization.adoc)).

### The two submission APIs

The legacy path packages the list as `VkSubmitInfo` and calls `vkQueueSubmit`. Timeline values use `VkTimelineSemaphoreSubmitInfo`. The synchronization2 path packages the same logical list as `VkSubmitInfo2`, `VkSemaphoreSubmitInfo`, and `VkCommandBufferSubmitInfo`, then calls `vkQueueSubmit2` or the KHR entry point in Vulkan SC builds. `SynchronizationWrapper` changes the packaging and entry point, not the dependency pattern.

## One Concrete Example

Each of four submit positions receives one base type:

| Type | Contents | Generated counterpart |
|---:|---|---|
| 0 | wait | signal only |
| 1 | wait and command buffer | command buffer and signal |
| 2 | wait and signal | signal, then wait |
| 3 | wait, command buffer, and signal | command buffer and signal, then wait |

For type 1, the original position waits and runs a read command buffer. The test creates a counterpart with the paired write command buffer and a signal. It submits the original and counterpart structures together. A four-digit case name such as `0123` records the type selected at each position.

## End-to-End Test Flow

```text
[host] choose a write operation, read operation, and first compatible resource
[host] choose one of 256 four-position submit-info combinations
[host] record paired write and read command buffers
[host] add the write-to-read resource barrier
[host] allocate binary semaphore pairs or one timeline semaphore with values
[host] generate counterpart submissions for the dependency chain
[host] submit the complete list to the universal queue through the selected wrapper
[device] execute the writes and reads in queue submission order
[host] wait for the fence
[host] compare paired results and decide pass/fail
```

The test uses random seed `1024`. Each present wait, command-buffer, or signal element gets a count from 2 through 10. Binary cases use one semaphore per wait-signal pair. Timeline cases share one semaphore and use increasing values with increments from 1 through 100.

## Generated Test Artifacts and Bound Resources

The source uses `COPY_BUFFER` and `SSBO_VERTEX` for both write and read operations. For each pair, it selects the first entry in `s_resources` supported by both operations and stops. The command buffers access that resource. The wrapper records the appropriate legacy or synchronization2 barrier and submit structures. The host waits on a fence and checks the operation output. Buffer results use `deMemCmp`; an indirect-buffer result must reach the expected counter value when that resource applies.

## What Is Checked

- The queue accepts the generated submit list and the fence reaches completion.
- Every paired read result matches the corresponding write result.
- Indirect-buffer results reach at least the expected counter value when applicable.
- Support checks reject missing timeline semaphore support, missing `VK_KHR_synchronization2`, or unsupported operation/resource combinations as `NotSupportedError`; those cases are not synchronization failures.

## Behavior Parameter Identification

> **Behavior parameter:** result and support outcome branch
>
> **Candidate values:** paired read result, timeline support, synchronization2 support, operation/resource support, queue or fence submission

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|---|---|
| Paired read result | The implementation did not preserve the dependency chain or queue submission order, or the selected resource operation produced incorrect data. |
| Timeline support | The device does not expose the `timelineSemaphore` feature. |
| Synchronization2 support | `VK_KHR_synchronization2` is unavailable. |
| Operation/resource support | The selected operation or resource needs a device feature that is not provided. |
| Queue or fence submission | The generated semaphore, command-buffer, or submit-info construction is invalid for the selected API path. |

## Important Variations and Special Cases

- `binary_semaphore` uses separate semaphores for each wait-signal pair.
- `timeline_semaphore` shares one semaphore and distinguishes dependencies with timeline values; it requires the timeline semaphore feature.
- The same test family runs as `synchronization.implicit` through the legacy wrapper and as `synchronization2.implicit` through the synchronization2 wrapper.
- The source tests four operation pairs and one compatible resource per pair. This keeps the submit permutation space bounded; it does not claim to cover every compatible resource.

## Source Mapping

| Topic | Source link | Why it matters |
|---|---|---|
| Submit element types and counterpart rules | [`QueueSubmitInfo`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L104-L150) | Defines the dependency invariants and binary/timeline distinction. |
| Execution and result checking | [`QueueSubmitImplicitTestInstance::iterate`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L174-L220) | Creates command buffers, submits work, waits, and checks results. |
| Support checks | [`QueueSubmitImplicitTestCase::checkSupport`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L591-L619) | Defines feature and operation support failures. |
| Operation/resource matrix | [`QueueSubmitImplicitTests::init`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L677-L743) | Defines the four operation pairs, first-compatible-resource rule, and 256 combinations. |
| Family registration | [`createImplicitSyncTests`](../../../modules/vulkan/synchronization/vktSynchronizationImplicitTests.cpp#L757-L767) | Registers the two semaphore test families. |
| API translation | [`LegacySynchronizationWrapper::queueSubmit`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L774-L834), [`Synchronization2Wrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L846-L870) | Shows the legacy and synchronization2 submission representations. |
| Specification context | [Synchronization and Cache Control](../../../../vulkan-docs/src/chapters/synchronization.adoc) | Grounds the distinction between limited implicit ordering and explicit resource synchronization. |

## Questions / Risk Points for User Audit

- Is the distinction between submit-order testing and the recorded resource barrier clear?
- Is the shared implementation and the two exact registered roots clear?
- Is the first-compatible-resource rule clear enough without enumerating generated leaves?
- Are support skips distinguished from failures of synchronization behavior?

## Conversion Notes for Final Wiki Rewrite

Keep the submission-order/resource-visibility distinction in `Background Knowledge`. Use the four submit types as the concrete parameter table, retain both category-qualified registration roots, and keep the two wrapper paths in the runtime and source appendix. The final page should use the copied failure mapping table above and explain cause analysis from the actual result checks rather than adding generic driver or hardware claims.
