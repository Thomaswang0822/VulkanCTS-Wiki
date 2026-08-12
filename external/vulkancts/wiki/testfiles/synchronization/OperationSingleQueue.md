## Overview

**Core question:** Does the selected synchronization primitive make a preceding write visible to a following read when both operations use one queue?

- This page covers the implementation in `vktSynchronizationOperationSingleQueueTests.cpp` and the shared operation/resource framework.
- The factory registers the same test families below both `synchronization.op.single_queue` and `synchronization2.op.single_queue`.
- Each case combines a write operation, a read operation, and a supported resource. The test compares what the write should produce with what the read observes.
- The `synchronization` root uses legacy synchronization commands. The `synchronization2` root uses the synchronization2 command and flag forms and adds sync2-specific variants.

## Background Knowledge

- A Vulkan memory dependency connects a source access to a destination access. The source and destination stage/access masks describe where the write and read occur; image dependencies also describe the layout transition. The test obtains these values from the selected operation implementations.
- Queue order alone does not describe all memory visibility needed by later accesses. The selected barrier, event, semaphore, or fence path must provide the dependency that lets the read observe the write. The Vulkan synchronization chapter defines the execution and memory-dependency rules used here: [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc).
- The legacy and synchronization2 APIs express the same test idea through different command and flag structures. A sync2 case therefore checks the synchronization2 path itself, including `VkPipelineStageFlags2KHR` and `VkAccessFlags2KHR` values.

## Registration Hierarchy

```text
synchronization.op.single_queue
├── fence
├── binary_semaphore
├── timeline_semaphore
├── barrier
└── event
```

The `multi_events` test family is registered under `synchronization2.op.single_queue` only. The trees show direct test families; operation-pair and resource descendants are generated below them.

## Parameter Dimensions and Observed Values

| Dimension | Registered values | Meaning in this test | Evidence |
|-----------|-------------------|----------------------|----------|
| Synchronization root | `synchronization.op.single_queue`, `synchronization2.op.single_queue` | Selects `LEGACY` or `SYNCHRONIZATION2` in the shared factory. | [`createSynchronizedOperationSingleQueueTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1293-L1300) |
| Synchronization primitive | `fence`, `binary_semaphore`, `timeline_semaphore`, `barrier`, `event` | Selects the test instance and dependency arrangement. | [`createTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1187-L1289) |
| Operation pair | `write_<operation>_read_<operation>` | Selects the source write, destination read, and their stage/access/layout requirements. | [`s_writeOps` and `s_readOps`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp#L36-L112) |
| Resource | Supported entries from `s_resources` | Selects buffer, image, indirect, index, or multisampled resource behavior. | [`s_resources`](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp#L36-L71) |
| Sync2 suffix | `_specialized_access_flag`, event `_maintenance9` | Adds specialized access masks or asymmetric event handling where the source and build support them. | [`createTests` variant generation](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1243-L1276) |
| Event queue suffix | `_cq` | Runs an eligible event case on a compute queue. | [`createTests` compute-queue branch](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1265-L1272) |
| Multi-event form | Two real events, or one real event plus `nop` | Exercises two-event waits and a null dependency in sync2. | [`createMultipleEventsTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1085-L1185) |

The default mustpass files contain 7,324 legacy leaves and 15,090 synchronization2 leaves for these roots. In the legacy root, `barrier`, `binary_semaphore`, `fence`, and `timeline_semaphore` each have 1,423 leaves, while `event` has 1,632. In the synchronization2 root, those four primitive families each have 2,634 leaves, while `event` has 4,266 and `multi_events` has 288. Unsupported operation/resource combinations do not create test cases.

## Behavior Parameters

The primary behavioral axis is the synchronization primitive. The operation pair and resource dimensions vary the memory dependency that the primitive must carry.

### `fence`: submission boundary

The test submits the write command buffer, waits for its fence, then submits the read command buffer. The result checks whether the read observes the completed write across this two-submission sequence. See [`FenceTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L732-L818).

### `binary_semaphore`: signal and wait

The write submission signals a binary semaphore and the read submission waits on it. The selected operation scopes still determine the resource access relationship. See [`BinarySemaphoreTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L458-L574).

### `timeline_semaphore`: chained values

The test places intermediate copy operations between the initial write and final read and advances a timeline semaphore through the chain. Each hop must preserve the data dependency. See [`TimelineSemaphoreTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L575-L731).

### `barrier`: one command-buffer dependency

The test records the write, a pipeline barrier built from the write and read `SyncInfo`, and the read in one command buffer. Image cases include the write-to-read layout transition. See [`BarrierTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L372-L457).

### `event`: set and wait

The test records the write, sets an event with a dependency, waits for it with the read dependency, and records the read. Eligible cases can use a compute queue. Sync2 event cases also cover specialized access and `VK_DEPENDENCY_ASYMMETRIC_EVENT_BIT_KHR` maintenance9 variants. See [`EventTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L76-L187).

### `multi_events`: two-event wait (sync2 only)

The test sets two events and waits on both before recording the reads. One generated form replaces either event with a `nop` event whose dependency contains no resource work. See [`EventsTestInstance`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L189-L370).

## Shader Analysis

Shader code is one possible implementation of the selected write or read operation, but this page has no single shader family whose code explains the synchronization test. The operation framework supplies stage/access information and builds the appropriate shader or transfer operation for each matrix entry. The relevant operation implementations are summarized in [`vktSynchronizationOperation.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp).

## Runtime Execution and Result Checking

- The test constructs `OperationContext`, a shared `Resource`, and write/read `Operation` objects. Resource usage is the union of the write output and read input usage flags.
- The selected operations record commands against that resource. For images, the dependency uses the operation layouts and the image subresource range. For buffers, it uses the buffer range.
- `SynchronizationWrapper` dispatches the common calls to legacy or synchronization2 commands. [`LegacySynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L381-L845) maps to legacy commands; [`Synchronization2Wrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L846-L916) maps to the synchronization2 forms.
- Sync2 variants require `VK_KHR_synchronization2`. Timeline cases require timeline semaphore support. Event cases check portability-subset event support when applicable, and `_maintenance9` cases require `VK_KHR_maintenance9`. Image format and sample-count support, operation support, and compute-queue availability prune unsupported cases.
- After completion, the test compares the write operation's `Data` with the read operation's `Data`. Standard resources require an exact byte match. Indirect buffers pass when the actual counter is at least the expected counter. A mismatch returns `fail`; a successful comparison returns `pass("OK")`.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `fence` | Incorrect ordering or visibility across the two fence-separated submissions; operation stage/access or resource handling is also implicated. |
| `binary_semaphore` | Incorrect semaphore signal/wait submission dependency or incomplete visibility for the selected resource access pair. |
| `timeline_semaphore` | Incorrect timeline value chaining, intermediate-copy dependency, or visibility across one of the hops. |
| `barrier` | Incorrect pipeline-barrier stage/access or image-layout dependency in the single command buffer. |
| `event` | Incorrect event set/wait dependency, event scope handling, image layout handling, or compute-queue path. |
| `multi_events` | Incorrect `vkCmdWaitEvents2KHR` handling when waiting on two event dependencies, including a null dependency. |

### Cause Analysis

#### Dependency scope does not cover the selected accesses

**Possible failure symptoms:** The read-side bytes differ from the write-side bytes, or an indirect read reports a counter below the expected value.

**Possible implementation causes:** The implementation may fail to apply the source/destination stage or access scopes required by the operation pair, or may mishandle an image layout transition. The test source derives these scopes from the operation implementations; a specific implementation cause needs investigation against that operation and the Vulkan synchronization rules.

#### Primitive-specific ordering or signal handling is incorrect

**Possible failure symptoms:** A fence, binary semaphore, timeline semaphore, or event case reaches the final comparison with stale or incomplete data. Timeline failures can identify a particular hop only through the aggregate result check.

**Possible implementation causes:** The implementation may mishandle the selected synchronization object's signal, wait, timeline value, event dependency, or submission sequencing. The source confirms the command arrangement, but it does not assign a failure to a particular driver, hardware, compiler, or host component.

#### Synchronization2 or special event path is incorrect

**Possible failure symptoms:** A sync2-only specialized-access, maintenance9, compute-queue, or multi-event leaf fails its same data comparison, including a two-event case with a `nop` dependency.

**Possible implementation causes:** The implementation may mishandle the synchronization2 command entry point, `VkAccessFlags2KHR` interpretation, asymmetric event dependency, compute queue selection, or multiple-event dependency array. The exact cause requires investigation of the failing path and implementation behavior.

## Case Pruning

### Requirement-based pruning

- Sync2 cases require `VK_KHR_synchronization2`; timeline cases require timeline semaphore support.
- Event cases require the portability-subset event feature when that feature is exposed and disabled.
- `_maintenance9` requires `VK_KHR_maintenance9`; `_cq` requires a suitable compute queue.
- Image cases require supported format usage and sample counts. Every operation must support the selected resource.

### Design-based pruning

- The ordinary matrix includes only operation/resource pairs accepted by `isResourceSupported` for both operations.
- Sync2 suffixes are added only when the selected operation supports specialized access or when the event primitive selects maintenance9 behavior.
- `multi_events` uses four write operations, four read operations, and five resources rather than the full matrix. It generates both real-event pairs and one-real-event/no-op pairs to keep the two-event behavior focused.

## Key Takeaways

- The page tests one invariant across several synchronization mechanisms: the read must observe the preceding write for the selected operation scopes and resource.
- `synchronization.op.single_queue` and `synchronization2.op.single_queue` share the matrix but exercise different API paths; sync2 also expands event and access-flag coverage.
- The expected result comes from the write operation, while the actual result comes from the read operation. Exact byte comparison is the normal check; indirect counters use a lower-bound check.
- A passing case shows that this particular operation/resource combination completed with the selected dependency. A failure identifies an observable synchronization result, not a predetermined bug location.

## Source Reference Appendix

| Entry point | Link | Why it matters |
|-------------|------|----------------|
| Single-queue registration | [`createSynchronizedOperationSingleQueueTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1293-L1300) | Creates the `single_queue` group for either synchronization type. |
| Matrix and suffix generation | [`createTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1187-L1289) | Registers primitive, operation/resource, sync2 suffix, and compute-queue variants. |
| Two-event generation | [`createMultipleEventsTests`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L1085-L1185) | Registers sync2 `multi_events` cases. |
| Primitive implementations | [`vktSynchronizationOperationSingleQueueTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationSingleQueueTests.cpp#L76-L818) | Contains event, barrier, binary semaphore, timeline semaphore, and fence execution. |
| Shared operation behavior | [`vktSynchronizationOperation.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperation.cpp) | Builds operations, stage/access scopes, layouts, data, and generated programs. |
| Command dispatch | [`vktSynchronizationUtil.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.cpp#L381-L916) | Selects legacy versus synchronization2 Vulkan calls. |
| Resource descriptions | [`vktSynchronizationOperationResources.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationResources.hpp#L36-L71) | Defines resources used by the matrix. |
| Legacy mustpass | [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt) | Lists `dEQP-VK.synchronization.op.single_queue` leaves. |
| Sync2 mustpass | [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt) | Lists `dEQP-VK.synchronization2.op.single_queue` leaves, including sync2-only variants. |
| Vulkan synchronization semantics | [`synchronization.adoc`](../../../../vulkan-docs/src/chapters/synchronization.adoc) | Defines the memory and execution dependency model used to interpret the checks. |
