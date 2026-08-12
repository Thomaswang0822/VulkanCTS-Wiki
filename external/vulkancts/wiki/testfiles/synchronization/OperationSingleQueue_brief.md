# Understanding Brief: single-queue synchronization operation tests

## One-Sentence Test Purpose

This test checks whether a write followed by a read on one Vulkan queue observes the required memory dependency when the test selects a fence, semaphore, pipeline barrier, or event synchronization mechanism.

## Background Knowledge

### Execution order and memory dependencies

Submitting commands to one queue gives them queue order, but the test still supplies synchronization information that makes the write available and the read visible at the stages and access types selected by the operations. A memory dependency therefore has two parts: the source operation and its `stageMask`/`accessMask`, and the destination operation and its corresponding masks. For images it also carries the old and new layouts.

Why it matters here:
- `Operation::getOutSyncInfo()` describes the write side and `Operation::getInSyncInfo()` describes the read side.
- The barrier or event dependency uses those values; a semaphore or fence also orders submissions, while the operation-specific memory dependency supplies the resource access relationship.

### Legacy and synchronization2 command forms

The test uses the same operation matrix for `SynchronizationType::LEGACY` and `SynchronizationType::SYNCHRONIZATION2`. The wrapper selects legacy commands such as `vkCmdPipelineBarrier`, `vkCmdSetEvent`, and `vkCmdWaitEvents` for the former, and `vkCmdPipelineBarrier2KHR`, `vkCmdSetEvent2KHR`, and `vkCmdWaitEvents2KHR` for the latter. The synchronization2 path represents stage and access scopes with the `VkPipelineStageFlags2KHR` and `VkAccessFlags2KHR` forms and can exercise specialized access flags.

Why it matters here:
- A passing legacy case does not by itself cover the synchronization2 command and flag path.
- The sync2-only suffixes are behavior variants, not alternate spellings of the same test case.

## One Concrete Example

Consider a conceptual buffer case named `barrier.write_fill_buffer_read_copy_buffer.buffer_16384`:

```text
[device] fill the 16 KiB buffer
[device] issue a pipeline barrier from the fill operation's transfer write
        to the copy operation's transfer read
[device] copy the buffer contents
[host] compare the write-side expected bytes with the read-side bytes
```

The actual masks come from the selected operation implementations. The test does not assume that every pair uses transfer stages: shader writes and reads use the stage selected by the shader operation, and image cases also transition from the write layout to the read layout.

## End-to-End Test Flow

[host] select a write operation, read operation, resource, synchronization primitive, and optional variant
[host] construct one shared `Resource` with the union of the write output and read input usage flags
[host] build the operation objects and any pipeline programs
[host] check required functionality, image format/sample support, queue availability, and operation support
[host] record the write, the selected synchronization operation, and the read in the required command-buffer/submission arrangement
[device] execute the write and make its result available through the selected dependency
[device] execute the read and write its observed data to the operation's result storage
[host] wait for completion and obtain expected data from the write operation and actual data from the read operation
[host] compare bytes, or compare indirect-buffer counters using the test's lower-bound rule
[host] return pass or fail

The primitive changes the command arrangement:
- `barrier` records write, pipeline barrier, and read in one command buffer.
- `event` records write, sets an event, waits for it with a dependency, then records read in one command buffer.
- `binary_semaphore` uses a signal after the write submission and a wait before the read submission.
- `fence` submits the write, waits for the fence, then submits the read.
- `timeline_semaphore` chains the write, intermediate copy operations, and read with increasing timeline values.
- `multi_events` (sync2 only) records two event dependencies, waits on both, then records the reads; one event may be a no-op.

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The operation framework creates program sources and pipelines for shader-based operations and initializes them through the selected `OperationSupport`. Timeline cases also initialize their intermediate copy operations. The test shares `PipelineCacheData` between cases to reuse compiled pipeline data; this does not change the synchronization contract.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Buffer resource | yes | yes | yes | through operation data | Tests buffer access pairs, including indirect buffers and index input. |
| Image resource | yes | yes | yes | through operation data | Adds image layout and subresource-range handling to the dependency. |
| Operation result/readback storage | yes | indirectly | written by read operation | yes | Supplies `actual` data for comparison with the write operation's `expected` data. |
| `VkFence`, `VkSemaphore`, or `VkEvent` | yes | synchronization object | controls ordering/dependency | no | Selects the primitive-specific synchronization path. |

The full resource table is defined by `s_resources` in [`vktSynchronizationOperationResources.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp#L36). The full operation tables are `s_writeOps` and `s_readOps` in [`vktSynchronizationOperationTestData.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp#L36).

## What Is Checked

- Standard buffers and images must produce identical expected and actual byte ranges, checked with `deMemCmp`.
- An indirect-buffer read must produce a counter at least as large as the expected counter. The test intentionally uses a lower bound because indirect counts are monotonic.
- Any mismatch returns `tcu::TestStatus::fail`; otherwise the case returns `pass("OK")`.

## Behavior Parameter Identification

> **Behavior parameter:** synchronization primitive/test family
>
> **Candidate values:** `fence`, `binary_semaphore`, `timeline_semaphore`, `barrier`, `event`, `multi_events` (sync2 only)

The write/read operation pair and resource form the coverage matrix, but the primary behavioral axis is the synchronization mechanism. `multi_events` is a separate sync2 mechanism with two-event and no-op-event cases.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fence` | Incorrect ordering or visibility across the two fence-separated submissions; operation stage/access or resource handling is also implicated. |
| `binary_semaphore` | Incorrect semaphore signal/wait submission dependency or incomplete visibility for the selected resource access pair. |
| `timeline_semaphore` | Incorrect timeline value chaining, intermediate-copy dependency, or visibility across one of the hops. |
| `barrier` | Incorrect pipeline-barrier stage/access or image-layout dependency in the single command buffer. |
| `event` | Incorrect event set/wait dependency, event scope handling, image layout handling, or compute-queue path. |
| `multi_events` | Incorrect `vkCmdWaitEvents2KHR` handling when waiting on two event dependencies, including a null dependency. |

## Important Variations and Special Cases

- Both registered roots are generated by the same `createSynchronizedOperationSingleQueueTests` factory. `synchronization.op.single_queue` uses `LEGACY`; `synchronization2.op.single_queue` uses `SYNCHRONIZATION2`.
- Sync2 adds `_specialized_access_flag` cases when either selected operation supports specialized access flags. These use specialized `VkAccessFlags2KHR` values such as shader storage or sampled read/write access instead of the broader shader access masks.
- Sync2 event cases add `_maintenance9` variants when the build is not Vulkan SC. They require `VK_KHR_maintenance9` and set `VK_DEPENDENCY_ASYMMETRIC_EVENT_BIT_KHR`.
- Event cases add `_cq` when both operations and the resource support a compute queue. This variant exists in both legacy and sync2 roots.
- Timeline cases require timeline-semaphore support. Sync2 roots require `VK_KHR_synchronization2`; event cases also respect portability-subset event support. Unsupported image formats/sample counts and unavailable compute queues are pruned at support checking.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Registration and matrix generation | [`createTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1187-L1289) | Defines primitive groups, operation/resource loops, sync2 variants, and `_cq`. |
| Registered roots | [`createSynchronizedOperationSingleQueueTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1293-L1300) | Creates `single_queue` for the selected synchronization type. |
| Primitive execution | [`EventTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L76-L187), [`BarrierTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L372-L457), [`BinarySemaphoreTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L458-L574), [`TimelineSemaphoreTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L575-L731), [`FenceTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L732-L818) | Shows command ordering and result checks. |
| Two-event cases | [`createMultipleEventsTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1085-L1185) | Defines the sync2-only matrix and no-op event names. |
| Operation scopes | [`Operation::getInSyncInfo`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp#L1415-L1429) and operation-specific `getOutSyncInfo` implementations | Supplies stage/access/layout information used by dependencies. |
| Legacy/sync2 dispatch | [`SynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L381-L916) | Maps the common wrapper calls to legacy or synchronization2 Vulkan commands. |
| Vulkan synchronization semantics | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc) | Defines execution and memory dependencies, availability/visibility, barriers, events, fences, and semaphores. |
| Mustpass coverage | [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt) and [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt) | Confirms both registered roots and generated leaf suffixes. |

## Questions / Risk Points for User Audit

- Is the distinction between queue ordering, execution dependency, and memory visibility clear enough for the final page?
- Should the final page include a full operation/resource inventory, or is the matrix description sufficient?
- Are the `_maintenance9`, `_specialized_access_flag`, and `_cq` suffix meanings clear without implying that all combinations exist?
- Does the two-event no-op example explain why `multi_events` is separate from the five primitive groups?

## Conversion Notes for Final Wiki Rewrite

- Keep the concrete barrier sequence as the representative mechanism example; describe the other primitives as controlled changes to submission or command-buffer ordering.
- Retain the concise resource table and the explicit legacy versus sync2 distinction.
- Carry the behavior parameter and failure mapping into the final page. Write cause analysis separately from this brief.
- Put source and mustpass links in the appendix, not in the opening explanation.
