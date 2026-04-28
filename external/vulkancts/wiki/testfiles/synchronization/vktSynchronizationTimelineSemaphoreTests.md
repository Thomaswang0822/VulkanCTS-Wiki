# [vktSynchronizationTimelineSemaphoreTests.cpp](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1)

## Overview

This file implements conformance tests for Vulkan timeline semaphores, covering host/device wait operations, serialized device-host synchronization chains, out-of-order queue submissions, one-to-N signaling patterns, sparse bind interactions, and miscellaneous edge cases. It is a very large file (3000+ lines) with two separate factory functions: [`createTimelineSemaphoreTests()`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L2939) for the LEGACY category and [`createSynchronization2TimelineSemaphoreTests()`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L2961) for the synchronization2 category.

## Role of File

This file contributes the `timeline_semaphore` group to **both** the `synchronization` (LEGACY) and `synchronization2` categories. The two factory functions build nearly identical test trees, differing only in the `SynchronizationType` parameter and a few LEGACY-only subgroups. Each test internally uses [`SynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp) to dispatch either `vkQueueSubmit` or `vkQueueSubmit2KHR` depending on the synchronization type.

## Source Code

| File | Description |
|------|-------------|
| [`vktSynchronizationTimelineSemaphoreTests.cpp`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1) | Implementation |
| [`vktSynchronizationTimelineSemaphoreTests.hpp`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.hpp#L1) | Public header declaring both factory functions |

## Registration Path

### synchronization (LEGACY)

```text
synchronization.timeline_semaphore
├── device_host
│   ├── <writeOp>_<readOp>
│   │   └── <resource>
│   └── misc
│       ├── max_difference_value
│       └── initial_value
├── one_to_n
│   └── <writeOp>_<readOp>
│       └── <resource>
├── wait_before_signal
│   └── <writeOp>_<readOp>
│       └── <resource>
├── wait
│   ├── all_signal_from_device
│   ├── one_signal_from_device
│   ├── all_signal_from_host
│   ├── one_signal_from_host
│   ├── host_wait_before_signal
│   ├── poll_signal_from_device
│   └── poll_signal_from_host
├── sparse_bind                  [not in Vulkan SC]
│   ├── no_sems
│   ├── no_wait_sig
│   ├── wait_no_sig
│   ├── wait_and_sig
│   └── wait_and_sig_2
└── misc
    └── ignore_timeline_semaphore_info
```

Source: [`createTimelineSemaphoreTests()`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L2939) with `SynchronizationType::LEGACY`.

### synchronization2 (SYNCHRONIZATION2)

```text
synchronization2.timeline_semaphore
├── device_host
│   ├── <writeOp>_<readOp>
│   │   └── <resource>
│   └── misc
│       └── max_difference_value
├── one_to_n
│   └── <writeOp>_<readOp>
│       └── <resource>
├── wait_before_signal
│   └── <writeOp>_<readOp>
│       └── <resource>
└── wait
    ├── all_signal_from_device
    ├── one_signal_from_device
    ├── all_signal_from_host
    ├── one_signal_from_host
    ├── host_wait_before_signal
    ├── poll_signal_from_device
    └── poll_signal_from_host
```

Source: [`createSynchronization2TimelineSemaphoreTests()`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L2961) with `SynchronizationType::SYNCHRONIZATION2`.

**Differences from LEGACY**: The synchronization2 tree omits `sparse_bind` (Vulkan SC guard) and the `misc.initial_value` subtest. The `device_host` group uses [`Sytnchronization2DeviceHostTests`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1245) instead of [`LegacyDeviceHostTests`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1225).

## Test Families

### WaitTests -- `wait`

Tests basic `vkWaitSemaphores` / `vkWaitSemaphoresKHR` behavior with timeline semaphores.

| Test Case | Parameters | Description |
|-----------|------------|-------------|
| `all_signal_from_device` | waitAll=true, signalFromDevice=true | Wait for all semaphores signaled from device |
| `one_signal_from_device` | waitAll=false, signalFromDevice=true | Wait for any semaphore signaled from device |
| `all_signal_from_host` | waitAll=true, signalFromDevice=false | Wait for all semaphores signaled from host |
| `one_signal_from_host` | waitAll=false, signalFromDevice=false | Wait for any semaphore signaled from host |
| `host_wait_before_signal` | -- | Host waits on a timeline point that is itself waiting for a signal; verifies VK_TIMEOUT before signal, VK_SUCCESS after |
| `poll_signal_from_device` | signalFromDevice=true | Polls `vkGetSemaphoreCounterValue` until signaled from device |
| `poll_signal_from_host` | signalFromDevice=false | Polls `vkGetSemaphoreCounterValue` until signaled from host |

### DeviceHostTests -- `device_host`

Creates a chain of serialized GPU-write, GPU-read, host-copy operations using a single timeline semaphore. A host thread waits for the GPU read, copies data, then signals the next GPU write. Verifies data integrity across the entire chain.

Two subclasses:
- [`LegacyDeviceHostTests`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1225) -- adds `misc.max_difference_value` and `misc.initial_value`
- [`Sytnchronization2DeviceHostTests`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1245) -- adds only `misc.max_difference_value`

### WaitBeforeSignalTests -- `wait_before_signal`

Submits GPU operations out-of-order to multiple queues, then signals the first timeline value from the host. Verifies that the chain of dependent operations completes correctly despite being submitted before the signal.

### OneToNTests -- `one_to_n`

Tests one-to-N signaling: a single write operation signals a timeline semaphore, which then fans out to multiple copy and read operations on different queues. Verifies that all readers observe the correct data.

### SparseBindGroup -- `sparse_bind` (LEGACY-only, not in Vulkan SC)

Tests `vkQueueBindSparse` combined with timeline semaphore wait/signal. Parameterized by the number of wait and signal semaphores.

| Test Case | Wait Semaphores | Signal Semaphores |
|-----------|----------------|-------------------|
| `no_sems` | 0 | 0 |
| `no_wait_sig` | 0 | 1 |
| `wait_no_sig` | 1 | 0 |
| `wait_and_sig` | 1 | 1 |
| `wait_and_sig_2` | 2 | 2 |

### misc -- `ignore_timeline_semaphore_info`

Verifies that `VkTimelineSemaphoreSubmitInfo` is correctly ignored when no timeline semaphores are present in the submit. Uses binary semaphores with a deliberately mismatched `VkTimelineSemaphoreSubmitInfo` pNext to confirm the driver does not read beyond array bounds.

## Parameter Dimensions

### Operation Pairs (device_host, wait_before_signal, one_to_n)

These families iterate over the full cross-product of write and read operations:

**Write Operations (19)**:
`COPY_BUFFER`, `COPY_BUFFER_TO_IMAGE`, `COPY_IMAGE_TO_BUFFER`, `COPY_IMAGE`, `BLIT_IMAGE`, `SSBO_VERTEX`, `SSBO_TESSELLATION_CONTROL`, `SSBO_TESSELLATION_EVALUATION`, `SSBO_GEOMETRY`, `SSBO_FRAGMENT`, `SSBO_COMPUTE`, `SSBO_COMPUTE_INDIRECT`, `IMAGE_VERTEX`, `IMAGE_TESSELLATION_CONTROL`, `IMAGE_TESSELLATION_EVALUATION`, `IMAGE_GEOMETRY`, `IMAGE_FRAGMENT`, `IMAGE_COMPUTE`, `IMAGE_COMPUTE_INDIRECT`

**Read Operations (28)**:
`COPY_BUFFER`, `COPY_BUFFER_TO_IMAGE`, `COPY_IMAGE_TO_BUFFER`, `COPY_IMAGE`, `BLIT_IMAGE`, `UBO_VERTEX`, `UBO_TESSELLATION_CONTROL`, `UBO_TESSELLATION_EVALUATION`, `UBO_GEOMETRY`, `UBO_FRAGMENT`, `UBO_COMPUTE`, `UBO_COMPUTE_INDIRECT`, `SSBO_VERTEX`, `SSBO_TESSELLATION_CONTROL`, `SSBO_TESSELLATION_EVALUATION`, `SSBO_GEOMETRY`, `SSBO_FRAGMENT`, `SSBO_COMPUTE`, `SSBO_COMPUTE_INDIRECT`, `IMAGE_VERTEX`, `IMAGE_TESSELLATION_CONTROL`, `IMAGE_TESSELLATION_EVALUATION`, `IMAGE_GEOMETRY`, `IMAGE_FRAGMENT`, `IMAGE_COMPUTE`, `IMAGE_COMPUTE_INDIRECT`, `INDIRECT_BUFFER_DRAW`, `INDIRECT_BUFFER_DRAW_INDEXED`, `INDIRECT_BUFFER_DISPATCH`, `VERTEX_INPUT`

### Resources

Each write/read pair is further iterated over [`s_resources`](../../../modules/vulkan/synchronization/vktSynchronizationOperationTestData.hpp) entries that support both operations. Only compatible resource types are included.

### SynchronizationType

Every test case is instantiated for both `LEGACY` and `SYNCHRONIZATION2` via the two factory functions.

## Support / Feature Requirements

| Requirement | Applicable Tests |
|-------------|-----------------|
| `VK_KHR_timeline_semaphore` | All tests in this file |
| `VK_KHR_synchronization2` | All tests when `SynchronizationType::SYNCHRONIZATION2` |
| `VK_KHR_sparse_bind` | `sparse_bind` subgroup (LEGACY-only) |
| `timelineSemaphore` feature | Checked via `context.getTimelineSemaphoreFeatures()` |
| `maxTimelineSemaphoreValueDifference` property | `misc.max_difference_value` |

## Verification Methods

- **Data comparison**: For buffer resources, `deMemCmp` compares write-output data against read-output data. For indirect buffers, the counter value is checked to be at least the expected value.
- **Semaphore counter polling**: `vkGetSemaphoreCounterValue` is polled in a loop to verify the counter advances to the expected value.
- **Wait result checking**: `vkWaitSemaphores` return values are checked against `VK_SUCCESS` or `VK_TIMEOUT` as appropriate.
- **Initial value verification**: `vkGetSemaphoreCounterValue` is checked against the expected initial value (0 or `nonZeroMaxValue`).

## Test Principles

- **Timeline value chains**: Tests construct chains of timeline values (write < read < cpu) to enforce ordering between GPU and host operations without binary semaphores.
- **Host-device handoff**: The `device_host` family uses a dedicated host thread ([`HostCopyThread`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L790)) to wait on GPU reads, copy data, and signal the next GPU write, exercising the full timeline semaphore lifecycle.
- **Out-of-order submission**: `wait_before_signal` submits dependent GPU work before the signal exists, then signals from the host to kick off the chain.
- **Fan-out signaling**: `one_to_n` tests that a single timeline signal can correctly synchronize multiple downstream readers.
- **API variant abstraction**: [`SynchronizationWrapper`](../../../modules/vulkan/synchronization/vktSynchronizationUtil.hpp) abstracts `vkQueueSubmit` vs `vkQueueSubmit2KHR`, allowing the same test logic to cover both API paths.
- **Shared pipeline cache**: [`PipelineCacheData`](../../../modules/vulkan/synchronization/vktSynchronizationTests.cpp#L93) is shared across operation pair tests to reduce shader compilation overhead.

## Notes / Uncertainties

- The class name `Sytnchronization2DeviceHostTests` contains a typo ("Sytnchronization2" instead of "Synchronization2") but this is the actual class name in the source code.
- The `sparse_bind` subgroup is guarded by `#ifndef CTS_USES_VULKANSC` and only appears in the LEGACY tree.
- The `misc.initial_value` subtest only exists in the LEGACY tree (inside [`LegacyDeviceHostTests`](../../../modules/vulkan/synchronization/vktSynchronizationTimelineSemaphoreTests.cpp#L1225)), not in the synchronization2 tree.
- The `ignore_timeline_semaphore_info` test is registered directly under `timeline_semaphore.misc` and is not guarded by a synchronization2 variant -- it uses the legacy `vkQueueSubmit` API directly.
- The file uses two separate factory functions rather than a single parameterized one, unlike `signal_order` and `implicit` which take a `SynchronizationType` parameter in their factory function.
