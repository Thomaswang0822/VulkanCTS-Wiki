# vktSynchronizationSignalOrderTests.cpp

## Overview

**Core question:** If twelve writes are submitted in order and a later read waits only for the last signal, does every read observe its corresponding write?

This page documents the `signal_order` family implemented in [`vktSynchronizationSignalOrderTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp). The same factory is used for both registered categories: `synchronization.signal_order` uses `SynchronizationType::LEGACY`, while `synchronization2.signal_order` uses `SynchronizationType::SYNCHRONIZATION2`. The wrapper in [`vktSynchronizationUtil.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp) selects the corresponding submit and barrier commands.

The test checks signal ordering together with explicit write-to-read memory barriers. Waiting for the final signal is therefore the ordering trigger; it is not a substitute for the source's operation-specific synchronization scopes.

## Registration hierarchy

```text
synchronization.signal_order
├── binary_semaphore
│   └── <writeOp>_<readOp>/<resource>
├── timeline_semaphore
│   └── <writeOp>_<readOp>/<resource>
├── shared_binary_semaphore
│   └── <writeOp>_<readOp>/<resource>_<externalSemaphoreType>
└── shared_timeline_semaphore
    └── <writeOp>_<readOp>/<resource>_<externalSemaphoreType>

synchronization2.signal_order
└── the same four-family tree
```

The four direct children are registered by [`createSignalOrderTests`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1632-L1645). The operation and resource levels are generated at group initialization; unsupported operation/resource pairs are omitted. The exact executable leaves are generated, so the mustpass files are the authoritative snapshot of currently materialized combinations: [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt) and [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt).

## Test families

### `binary_semaphore`

A single device uses two distinct queues. Each of twelve write command buffers is submitted as a separate submit entry and signals its own binary semaphore. One read command buffer contains all twelve reads and waits only on the last write semaphore.

### `timeline_semaphore`

The single-device flow is the same, but one timeline semaphore carries increasing values. A host signal releases the initial timeline value; the ordered submit entries signal later values, and the read submission waits for the final value. Timeline support is checked before execution.

### `shared_binary_semaphore`

The write queue runs on the context device and the read queue on a second logical device created through [`SingletonDevice`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L197). Each resource is exportable on the first device and imported on the second. The final binary semaphore is exported/imported across devices before the read submit.

### `shared_timeline_semaphore`

This is the shared-device flow with a timeline semaphore and increasing values. The source uses one exportable timeline semaphore per device path, imports the final signal into the read device, and waits for the final value.

## Generated dimensions

| Dimension | Values / rule |
|---|---|
| API path | `LEGACY` → `synchronization`; `SYNCHRONIZATION2` → `synchronization2` |
| Semaphore family | `binary_semaphore`, `timeline_semaphore`, `shared_binary_semaphore`, `shared_timeline_semaphore` |
| Write operation | 19 values: copy buffer, buffer/image copies, blit, SSBO vertex/tessellation-control/tessellation-evaluation/geometry/fragment/compute/compute-indirect, and image vertex/tessellation-control/tessellation-evaluation/geometry/fragment/compute/compute-indirect |
| Read operation | 30 values: copy buffer, buffer/image copies, blit, UBO vertex/tessellation-control/tessellation-evaluation/geometry/fragment/compute/compute-indirect, SSBO vertex/tessellation-control/tessellation-evaluation/geometry/fragment/compute/compute-indirect, image vertex/tessellation-control/tessellation-evaluation/geometry/fragment/compute/compute-indirect, indirect draw, indexed indirect draw, indirect dispatch, and vertex input |
| Resource | Entries from `s_resources` compatible with both selected operations |
| Shared handle pair | Opaque FD; opaque Win32 KMT; opaque Win32. Memory and semaphore handle types are paired. |

Operation names in generated paths use the source's `getOperationName()` spelling. Do not infer a fixed number of resource leaves: compatibility and implementation support determine which pairs are materialized.

## Runtime sequence

1. The test selects queues capable of the write and read operations. Non-shared cases require two different queues on one device; if no suitable second queue exists, the case is unsupported.
2. It creates twelve resource/operation pairs and records each write in its own command buffer. Each command buffer ends with a barrier from the write operation's stage/access scope to the read operation's scope; images also carry the required layout transition.
3. It records all twelve reads in one command buffer. In the shared path it unions their destination stage masks for the final wait; the non-shared path uses the wrapper's top-of-pipe wait stage.
4. It submits the writes together as twelve ordered submit entries. Binary entries signal separate semaphores; timeline entries use increasing values and the initial host signal.
5. It submits the read command buffer with a wait for only the final write signal, then waits for the read completion. Shared cases perform the equivalent operation on the imported resources and semaphore on device B.
6. It compares each read result with the corresponding write result and waits for device idle before resource destruction. [`DeviceWaitIdleGuard`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L87-L103) protects teardown.

## Support and pruning

- Timeline families require timeline semaphore feature support.
- `synchronization2` cases require `VK_KHR_synchronization2`.
- Shared cases require exportable/importable external memory and semaphores for the selected resource and handle pair; the source queries external properties and skips unsupported combinations.
- Shared semaphore cases intentionally exclude copy-semantics handles such as sync FD. The registered shared handle cases are opaque FD, opaque Win32 KMT, and opaque Win32, subject to platform availability.
- The source's custom second-device setup enables the functionality needed by the shared path and obtains a universal queue. It does not turn an unavailable external-memory or external-semaphore capability into a runnable case.

## Verification and failure meaning

For ordinary buffer and image results, expected data from the write operation is compared with data produced by the read operation using `deMemCmp`. For indirect buffers, the observed counter must be at least the expected value. A failing leaf indicates that the complete tested chain—submission ordering, semaphore wait/signal behavior, explicit barrier scopes/layouts, queue/device sharing, and the selected operation—did not produce the expected result. The result alone cannot isolate which mechanism is at fault.

## Source map

| Topic | Evidence |
|---|---|
| Factory and four families | [`createSignalOrderTests`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1632-L1645) |
| Non-shared generated matrix | [`QueueSubmitSignalOrderTests::init`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1522-L1617) |
| Shared matrix and handle pairs | [`QueueSubmitSignalOrderSharedTests::init`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L975-L1094) |
| Non-shared execution | [`QueueSubmitSignalOrderTestInstance::iterate`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L1198-L1470) |
| Shared execution and import/export | [`QueueSubmitSignalOrderSharedTestInstance::iterate`](../../../modules/vulkan/synchronization/vktSynchronizationSignalOrderTests.cpp#L431-L815) |
| Operation/resource definitions | [`vktSynchronizationOperationTestData.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp#L36-L112) and `s_resources` in the synchronization operation resources headers |
| API abstraction | [`vktSynchronizationUtil.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp) |
| Registered leaves | [`synchronization.txt`](../../../mustpass/main/vk-default/synchronization.txt) and [`synchronization2.txt`](../../../mustpass/main/vk-default/synchronization2.txt) |

## Key takeaways

- The test deliberately submits twelve writes in one ordered queue-submit call and waits only for the final signal.
- Explicit operation-specific barriers connect each write to its corresponding read.
- Binary and timeline semaphore families cover both one-signal-per-iteration and increasing-value signaling.
- Shared families additionally test external memory and semaphore import/export across two logical devices.
- Both category roots are covered by one implementation page; their API submission path is selected by `SynchronizationType`.
