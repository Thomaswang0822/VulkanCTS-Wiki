## Overview

**Core question:** Can a Vulkan implementation enumerate performance counters and write results for single and simultaneous performance query pools through the permitted retrieval paths?

- This page documents the `performance_query` test family in the `query_pool` test category, implemented by [`vktQueryPoolPerformanceTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp).
- The family covers counter enumeration and metadata checks, one-pool query execution, and two-pool query execution.
- Each behavior has graphics and compute leaves. Query-execution leaves also have host-get and command-buffer-copy result paths.
- The test checks metadata consistency and whether every enabled result element was overwritten. It does not assign a required numeric value to a performance counter.

## Background Knowledge

- A performance query pool selects counters for one queue family. `vkGetPhysicalDeviceQueueFamilyPerformanceQueryPassesKHR` reports how many passes a selection needs. The application submits the recorded workload once per pass with the corresponding `VkPerformanceQuerySubmitInfoKHR` pass index.
- A performance counter has a scope. Query-execution tests exclude `VK_PERFORMANCE_COUNTER_SCOPE_COMMAND_BUFFER_KHR` because their query begins and ends around a draw or dispatch, rather than at command-buffer boundaries. The enumeration tests still enumerate and validate counters with every scope.
- Results can reach host-visible memory through `vkGetQueryPoolResults` or through `vkCmdCopyQueryPoolResults`. Command-buffer copying is available only when `allowCommandBufferQueryCopies` is true.

## Registration Hierarchy

```text
query_pool.performance_query
├── enumerate_and_validate_compute
├── enumerate_and_validate_compute_copy
├── enumerate_and_validate_graphic
├── enumerate_and_validate_graphic_copy
├── multiple_pools_compute
├── multiple_pools_compute_copy
├── multiple_pools_graphic
├── multiple_pools_graphic_copy
├── query_compute
├── query_compute_copy
├── query_graphic
└── query_graphic_copy
```

[`QueryPoolPerformanceTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1356-L1386) creates the twelve test case leaves. The canonical mustpass list contains the same twelve leaves in [`query-pool.txt`](../../../mustpass/main/vk-default/query-pool.txt#L490-L501). The parent [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42-L55) registers this test family only outside `CTS_USES_VULKANSC`.

## Parameter Dimensions and Observed Values

| Dimension | Values | Effect |
|-----------|--------|--------|
| Test behavior | `enumerate_and_validate`, `query`, `multiple_pools` | Selects metadata validation, one pool, or two concurrent pools. |
| Workload | `graphic`, `compute` | Selects a queried triangle draw or a queried `2 x 2 x 2` compute dispatch. |
| Retrieval suffix | no suffix, `_copy` | Selects host `vkGetQueryPoolResults` or command-buffer `vkCmdCopyQueryPoolResults` for query-execution cases. |
| Pool counter selection | all eligible counters; alternate subsets | A single pool selects every eligible counter. Two pools use `createQueryPool(0, 2)` and `createQueryPool(1, 2)` to select complementary alternating sets. |
| Profiling passes | device-reported count | The recorded workload is resubmitted for each required pass. |

The `_copy` registration suffix is applied to all three behaviors by the shared registration loop. [`EnumerateAndValidateTest`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L150-L239) never retrieves query results, so its `_copy` leaves do not issue `vkCmdCopyQueryPoolResults`.

For query execution, the `graphic` and `compute` names select the workload class. Counter enumeration, pool creation, and submission use the CTS universal queue family, as shown in [`QueryTestBase::setupCounters()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L273-L302) and [`createQueryPool()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L304-L378).

## Behavior Parameters

The primary behavior parameter is test behavior: `enumerate_and_validate`, `query`, or `multiple_pools`.

### enumerate_and_validate: counter metadata

The test visits every queue family whose flags include the requested graphics or compute bit. For each family that reports counters, it requests a deliberately short list when more than one counter exists and requires `VK_INCOMPLETE`. It then checks the full count, unique UUIDs, valid scope/storage/unit enum ranges, and only the permitted description-flag bits.

### query: one selected counter set

The test removes command-buffer-scope counters, enables every remaining counter in one pool, resets query zero, and places a query around one graphics draw or compute dispatch. It executes all required profiling passes, then verifies the one pool's result memory.

### multiple_pools: two selected counter sets

The test creates two pools whose enabled-counter lists alternate through the eligible list. It resets both pools and records one queried workload per pool. It submits the command buffer for each required pass, then verifies each pool independently. This behavior requires simultaneous performance-query-pool support.

## Shader Analysis

The shaders only provide bounded graphics or compute work inside the query interval. The graphics path draws a triangle; the compute path increments storage-buffer entries. The test does not inspect shader output or use shader behavior to derive expected counter values, so a shader walkthrough would not explain the pass condition.

## Runtime Execution and Result Checking

For query-execution behaviors, the common sequence is:

1. Enumerate counters for the universal queue family, discard command-buffer-scope counters, select the counters for the pool or pools, and obtain the required pass count.
2. Acquire the profiling lock, reset query zero in every pool, and record the queried draw or dispatch. In the two-pool behavior, the command buffer contains two queried workloads, one for each pool.
3. Submit the recorded workload once per required pass. Each submission chains a `VkPerformanceQuerySubmitInfoKHR` with that pass index and waits for its fence.
4. Retrieve the result of each pool with `VK_QUERY_RESULT_WAIT_BIT`.

[`verifyQueryResults()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L417-L466) initializes a host-visible result buffer with random nonzero bytes. In host-get mode it calls [`vkGetQueryPoolResults`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L447-L451). In copy mode it records [`vkCmdCopyQueryPoolResults`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L432-L446), inserts a transfer-to-host memory barrier, submits, waits, and invalidates the allocation.

The verifier compares every `VkPerformanceCounterResultKHR` element with its original bytes. A result element that is unchanged fails the case. This is overwrite detection: it establishes that each enabled result slot was written, but it deliberately does not validate the measured counter's numeric semantics.

## Failure Meaning

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `enumerate_and_validate` | Counter enumeration count or incomplete-result handling is inconsistent, metadata contains duplicate UUIDs or invalid enum values, or description flags contain bits outside the permitted set. |
| `query` | Pool creation, reset, profiling-pass submission, query execution, or the selected result-retrieval path leaves an enabled result slot unwritten. |
| `multiple_pools` | Simultaneous pool support, alternating counter selection, independent query execution, or independent result retrieval leaves a result slot unwritten. |

### Cause Analysis

#### Enumeration API or metadata inconsistency

**Possible failure symptoms:** A matching queue family reports a different final count than its initial count, a short enumeration does not return `VK_INCOMPLETE`, a UUID repeats, an enum lies outside its defined range, or an unsupported description flag is set.

**Possible implementation causes:** The enumeration implementation may report inconsistent count and array data, generate duplicate identifiers, or populate `VkPerformanceCounterKHR` or `VkPerformanceCounterDescriptionKHR` fields outside the extension contract. The source localizes these failures to the returned metadata rather than a query workload.

#### Single-pool execution or retrieval leaves a slot untouched

**Possible failure symptoms:** After all required passes, one `VkPerformanceCounterResultKHR` retains the random bytes used to initialize its destination element.

**Possible implementation causes:** The pool may have selected or created its counter set incorrectly; reset, begin/end recording, required-pass submission, or result transfer may fail to produce a write for an enabled counter. The check cannot distinguish these stages or establish an expected counter magnitude. Further implementation-level investigation is needed to isolate the stage.

#### Simultaneous pools do not produce independent writes

**Possible failure symptoms:** One or both result buffers retain an initial element in `multiple_pools_*`, even if a corresponding single-pool leaf passes.

**Possible implementation causes:** The complementary selections may be wrong, simultaneous-pool support may not preserve both query states, or one pool's execution or retrieval may interfere with the other. The source verifies the pools independently, so the failed buffer identifies the affected selected set but not a specific implementation layer.

## Case Pruning

### Requirement-based pruning

[`QueryPoolPerformanceTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1298-L1340) requires `VK_KHR_performance_query` and `performanceCounterQueryPools` for every leaf. It skips with a quality warning when the universal queue family reports no performance counters. Query-execution leaves also need at least one counter outside command-buffer scope.

`multiple_pools_*` additionally requires `performanceCounterMultipleQueryPools`. `_copy` leaves require `VkPhysicalDevicePerformanceQueryPropertiesKHR::allowCommandBufferQueryCopies`; the enumeration `_copy` leaves still encounter this support gate even though their instance does not copy results.

### Design-based pruning

The test uses a small draw or dispatch and does not compare counter magnitudes because supported counters and their meanings are implementation-specific. It excludes command-buffer-scope counters because its query boundaries intentionally surround work inside a command buffer. The whole test family is not registered for Vulkan SC.

## Key Takeaways

- The test family has twelve registered leaves: three behaviors, two workload types, and two registration suffixes.
- One-pool tests select every eligible counter; two-pool tests divide the eligible list into complementary alternating selections.
- Required profiling passes rerun the same recorded workload with successive pass indices.
- Result checking detects an unwritten output element. It does not claim that any particular performance value is correct.

## Source Reference Appendix

| Topic | Source reference |
|-------|------------------|
| Family declaration | [`vktQueryPoolPerformanceTests.hpp`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.hpp#L29-L45) |
| Counter enumeration validation | [`EnumerateAndValidateTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L150-L239) |
| Counter filtering, selection, and pool creation | [`QueryTestBase::setupCounters()` and `createQueryPool()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L273-L378) |
| Host-get/copy retrieval and overwrite detection | [`QueryTestBase::verifyQueryResults()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L417-L466) |
| Graphics single/two-pool execution | [`GraphicQueryTest` and `GraphicMultiplePoolsTest`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L638-L887) |
| Compute single/two-pool execution | [`ComputeQueryTest` and `ComputeMultiplePoolsTest`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1014-L1219) |
| Support gates and leaf registration | [`QueryPoolPerformanceTest::checkSupport()` and `QueryPoolPerformanceTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1298-L1386) |
| Extension feature metadata | [`VK_KHR_performance_query.json`](../../../scripts/src/extensions/VK_KHR_performance_query.json) |
| Mustpass coverage | [`query-pool.txt`](../../../mustpass/main/vk-default/query-pool.txt#L490-L501) |
