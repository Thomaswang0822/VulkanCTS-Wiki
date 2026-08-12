# Brief: `vktSynchronizationTimelineSemaphoreTests.cpp`

- **Purpose:** exercise Vulkan timeline-semaphore ordering, host waits/signals, counter queries, and `VkTimelineSemaphoreSubmitInfo` handling.
- **Registration:** the source exposes two roots: `synchronization.timeline_semaphore` through `createTimelineSemaphoreTests()` (legacy submit path) and `synchronization2.timeline_semaphore` through `createSynchronization2TimelineSemaphoreTests()` (synchronization2 submit path).
- **Shared families:** `device_host`, `one_to_n`, `wait_before_signal`, and `wait` are present in both roots. Legacy additionally has `sparse_bind` (excluded by `CTS_USES_VULKANSC`) and `misc.ignore_timeline_semaphore_info`.
- **Generated coverage:** the three operation families enumerate 19 write operations × 28 read operations, retaining only operation/resource combinations supported by `s_resources`; each retained pair is grouped as `<write>_<read>/<resource>`.
- **Key checks:** data survives serialized GPU/host chains, fan-out, and pre-signal submission; waits return the expected success/timeout; counters reach expected values; the legacy device-host `initial_value` and both variants’ `max_difference_value` checks validate timeline properties.
- **Dependencies:** all cases require `VK_KHR_timeline_semaphore`; synchronization2 cases also require `VK_KHR_synchronization2`; operation-specific support is checked by the operation helpers. Sparse-bind cases use `vkQueueBindSparse` and are compiled out for Vulkan SC.
- **Source anchors:** factories at lines 2937–2969; operation/resource generation at `DeviceHostTestsBase` (1123–1262), `WaitBeforeSignalTests` (1809–1910), and `OneToNTests` (2354–2450); host handoff at `HostCopyThread` (790–853); API dispatch through `vktSynchronizationUtil.hpp`.
