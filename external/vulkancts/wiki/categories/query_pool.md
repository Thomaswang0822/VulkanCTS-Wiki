# Query Pool Tests

The `query_pool` category validates Vulkan query-pool functionality across occlusion, pipeline statistics, performance counters, concurrent multi-query usage, fragment-invocation-focused workloads, maintenance7 timestamp wrapping, and discard-related visibility behavior. It covers both host-side and command-buffer result retrieval paths, query reset workflows, inherited-query behavior, result layout handling, and several extension-specific features such as `VK_KHR_performance_query`, `VK_KHR_maintenance7`, `VK_KHR_device_address_commands`, and maintenance5 discard semantics.

## Source

- **Root registration:** [`vktQueryPoolTests.cpp`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp)
- **Build inventory:** [`CMakeLists.txt`](../../modules/vulkan/query_pool/CMakeLists.txt)

## Registration Entry Point

The [`createTests()`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L59) factory creates the top-level `query_pool` group. The internal [`createChildren()`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42) function adds 7 child subgroups, split between Vulkan-only and Vulkan+VKSC builds.

## Subgroup Structure

```text
query_pool
├── occlusion_query     (VK + VKSC)
├── statistics_query    (VK + VKSC)
├── performance_query   (VK only)
├── maintenance7        (VK only)
├── concurrent_queries  (VK + VKSC)
├── frag_invocations    (VK + VKSC)
└── discard             (VK + VKSC)
```

### VK / VKSC Split

| Group | VK | VKSC | Reason |
|-------|:--:|:----:|--------|
| `occlusion_query` | ✓ | ✓ | Always included in [`createChildren()`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L46) |
| `statistics_query` | ✓ | ✓ | Always included in [`createChildren()`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L47) |
| `performance_query` | ✓ | — | Registered only inside [`#ifndef CTS_USES_VULKANSC`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L48) |
| `maintenance7` | ✓ | — | Registered only inside the same non-SC guard in [`createChildren()`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L50) |
| `concurrent_queries` | ✓ | ✓ | Always included in [`createChildren()`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L52) |
| `frag_invocations` | ✓ | ✓ | Always included in [`createChildren()`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L53) |
| `discard` | ✓ | ✓ | Always included in [`createChildren()`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L54) |

## File Inventory

### Registration / Dispatcher

| File | Role |
|------|------|
| [`vktQueryPoolTests.cpp`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp) | Category root registration and subgroup dispatch |
| [`vktQueryPoolTests.hpp`](../../modules/vulkan/query_pool/vktQueryPoolTests.hpp) | Category header with [`createTests()`](../../modules/vulkan/query_pool/vktQueryPoolTests.hpp#L31) declaration |
| [`CMakeLists.txt`](../../modules/vulkan/query_pool/CMakeLists.txt) | Build split between shared VK/VKSC sources and Vulkan-only sources |

### Implementation Files

| File | Group(s) | Level-3 Doc |
|------|----------|-------------|
| [`vktQueryPoolOcclusionTests.cpp`](../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp) | `occlusion_query` | [vktQueryPoolOcclusionTests.md](../testfiles/query_pool/vktQueryPoolOcclusionTests.md) |
| [`vktQueryPoolStatisticsTests.cpp`](../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp) | `statistics_query` | [vktQueryPoolStatisticsTests.md](../testfiles/query_pool/vktQueryPoolStatisticsTests.md) |
| [`vktQueryPoolPerformanceTests.cpp`](../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp) | `performance_query` | [vktQueryPoolPerformanceTests.md](../testfiles/query_pool/vktQueryPoolPerformanceTests.md) |
| [`vktQueryMaintenance7Tests.cpp`](../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp) | `maintenance7` | [vktQueryMaintenance7Tests.md](../testfiles/query_pool/vktQueryMaintenance7Tests.md) |
| [`vktQueryPoolConcurrentTests.cpp`](../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp) | `concurrent_queries` | [vktQueryPoolConcurrentTests.md](../testfiles/query_pool/vktQueryPoolConcurrentTests.md) |
| [`vktQueryPoolFragInvocationTests.cpp`](../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp) | `frag_invocations` | [vktQueryPoolFragInvocationTests.md](../testfiles/query_pool/vktQueryPoolFragInvocationTests.md) |
| [`vktQueryPoolDiscardTests.cpp`](../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp) | `discard` | [vktQueryPoolDiscardTests.md](../testfiles/query_pool/vktQueryPoolDiscardTests.md) |

### Utility / Header Files (no Level-3 docs)

| File | Role |
|------|------|
| [`vktQueryPoolOcclusionTests.hpp`](../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.hpp) | Occlusion test class declaration |
| [`vktQueryPoolStatisticsTests.hpp`](../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.hpp) | Statistics test class declaration |
| [`vktQueryPoolPerformanceTests.hpp`](../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.hpp) | Performance test class declaration |
| [`vktQueryMaintenance7Tests.hpp`](../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.hpp) | Maintenance7 factory declaration |
| [`vktQueryPoolConcurrentTests.hpp`](../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.hpp) | Concurrent test class declaration |
| [`vktQueryPoolFragInvocationTests.hpp`](../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.hpp) | Fragment-invocation factory declaration |
| [`vktQueryPoolDiscardTests.hpp`](../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.hpp) | Discard factory declaration |

## Subgroup Summary

| Group | What It Verifies | Key Extensions / Features |
|-------|------------------|---------------------------|
| `occlusion_query` | Occlusion query correctness across result modes, reset modes, availability, stride, clear/blit/resolve paths, and no-attachment rendering | `VK_EXT_host_query_reset`, `VK_KHR_device_address_commands`, `occlusionQueryPrecise` |
| `statistics_query` | Pipeline statistics query correctness across compute and graphics counters, command-buffer modes, reset workflows, and result layouts | `pipelineStatisticsQuery`, `VK_EXT_host_query_reset`, `VK_KHR_device_address_commands` |
| `performance_query` | Performance counter enumeration, single-pool execution, and multi-pool execution with host-get and command-copy paths | `VK_KHR_performance_query` |
| `maintenance7` | Timestamp query 32-bit vs 64-bit relationship with and without maintenance7 feature enablement | `VK_KHR_maintenance7` |
| `concurrent_queries` | Simultaneous use of multiple query types in one workload without cross-interference | `pipelineStatisticsQuery`, timestamps, `inheritedQueries` |
| `frag_invocations` | Full-screen fragment workloads checked via precise occlusion or fragment-invocation statistics, including primary/secondary command buffers and shader variants | `pipelineStatisticsQuery`, `inheritedQueries`, `fragmentStoresAndAtomics`, `occlusionQueryPrecise` |
| `discard` | Occlusion-query behavior under fragment discard, sample mask, alpha-to-coverage, early-fragment-test, and depth-use combinations | maintenance5 properties, `extendedDynamicState3AlphaToCoverageEnable`, `occlusionQueryPrecise` |

## Cross-File Recurring Test Families

### Result Retrieval Split

Several subgroups validate both host-side and command-buffer result retrieval:

- `occlusion_query` mixes [`vkGetQueryPoolResults`](../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L821) and [`vkCmdCopyQueryPoolResults`](../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1077) through results-mode selection.
- `statistics_query` has explicit host-get vs command-copy axes in [`QueryPoolStatisticsTests::init()`](../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6388).
- `performance_query` duplicates all three logical behaviors for non-copy and `_copy` modes through [`copyCases`](../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1359).

### Reset Workflow Coverage

Query reset behavior recurs across multiple files:

- `occlusion_query` includes `get_reset`, `get_create_reset`, and `copy_reset` variants in [`QueryPoolOcclusionTests::init()`](../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1797).
- `statistics_query` mirrors large parts of its hierarchy into `host_query_reset`, `reset_before_copy`, and `reset_after_copy` groups in [`QueryPoolStatisticsTests::init()`](../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6322).
- `maintenance7` resets its one-slot timestamp pool before writing the timestamp in [`recordComands()`](../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp#L112).
- `concurrent_queries`, `frag_invocations`, and `discard` each reset their pools immediately before recording measured work in [`PrimaryCommandBufferConcurrentTestInstance::iterate()`](../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L349), [`testInvocations()`](../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L319), and [`QueryPoolDiscardTestInstance::iterate()`](../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L364).

### Primary vs Secondary Command Buffer Coverage

Several subgroups explicitly compare primary and secondary command buffer behavior:

- `statistics_query` repeatedly instantiates `PRIMARY`, `SECONDARY`, and `SECONDARY_INHERITED` modes via [`addChilds`](../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6227).
- `concurrent_queries` splits the whole group into `primary_command_buffer` and `secondary_command_buffer` in [`QueryPoolConcurrentTests::init()`](../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L912).
- `frag_invocations` creates `primary*` and `secondary*` cases under both `occlusion` and `frag_invs` in [`createFragInvocationTests()`](../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L471).

### Exact vs Conservative Verification

Query-pool tests frequently distinguish exact-count validation from weaker non-zero or lower-bound checks:

- `occlusion_query` accepts exact counts for precise mode and non-zero visibility for conservative mode in [`OcclusionQueryTestInstance::iterate()`](../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp#L1471).
- `frag_invocations` requires exact full-screen counts for `occlusion` but only lower bounds for `frag_invs` flat-shader cases in [`testInvocations()`](../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp#L370).
- `discard` uses exact counts in `precise` branches and non-zero validation in `none` branches in [`QueryPoolDiscardTestInstance::iterate()`](../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp#L411).
- `concurrent_queries` uses a slot-based zero vs non-zero rule for concurrent query captures in [`PrimaryCommandBufferConcurrentTestInstance::iterate()`](../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp#L445).

## Cross-File Recurring Parameter Dimensions

| Dimension | Subgroups | Typical Values |
|-----------|-----------|----------------|
| Query type | `occlusion_query`, `concurrent_queries`, `frag_invocations`, `maintenance7` | Occlusion, pipeline statistics, timestamp, performance |
| Result width | `occlusion_query`, `statistics_query`, `maintenance7` | 32-bit, 64-bit |
| Result path | `occlusion_query`, `statistics_query`, `performance_query` | Host get, command copy |
| Availability field | `occlusion_query`, `concurrent_queries` | Without availability, with availability |
| Command buffer mode | `statistics_query`, `concurrent_queries`, `frag_invocations` | Primary, secondary, inherited secondary |
| Reset mode | `occlusion_query`, `statistics_query`, `maintenance7` | Normal, host reset, reset before copy, reset after copy |
| Rendering variant | `occlusion_query`, `statistics_query`, `frag_invocations`, `discard` | No attachments, clear color/depth, blit, resolve, early tests, with/without depth |

## Cross-File Recurring Support Requirements

| Requirement | Subgroups |
|-------------|-----------|
| `occlusionQueryPrecise` | `occlusion_query`, `frag_invocations`, `discard` |
| `pipelineStatisticsQuery` | `statistics_query`, `concurrent_queries`, `frag_invocations` |
| `inheritedQueries` | `concurrent_queries`, `frag_invocations`, parts of `statistics_query` secondary inherited mode |
| Host/timestamp queue support | `concurrent_queries`, `maintenance7` |
| `VK_EXT_host_query_reset` | `occlusion_query`, `statistics_query` |
| `VK_KHR_device_address_commands` | `occlusion_query`, `statistics_query` |
| `VK_KHR_performance_query` | `performance_query` |
| `VK_KHR_maintenance7` | `maintenance7` |

## Cross-File Recurring Verification Methods

| Method | Subgroups |
|--------|-----------|
| Query result value comparison | All subgroups |
| Host-get / copied-buffer memory inspection | `occlusion_query`, `statistics_query`, `performance_query`, `maintenance7`, `discard` |
| Rendered image comparison | `frag_invocations`, `discard`, selected `occlusion_query` paths |
| Slot pairing / empty-vs-active capture validation | `concurrent_queries`, `occlusion_query` |
| Randomized destination-buffer overwrite detection | `performance_query` |
| 32-bit vs 64-bit cross-check | `maintenance7` |

## Notes

- The exact top-level registered children are only `occlusion_query`, `statistics_query`, `performance_query`, `maintenance7`, `concurrent_queries`, `frag_invocations`, and `discard`, in that order from [`createChildren()`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L46).
- The Vulkan / Vulkan SC split is structural at the top level only for `performance_query` and `maintenance7`; the other groups keep the same top-level names and handle most support differences inside their own implementations.
- [`CMakeLists.txt`](../../modules/vulkan/query_pool/CMakeLists.txt:7) mirrors that split by placing shared sources in `DEQP_VK_VKSC_QUERY_POOL_SRCS` and Vulkan-only sources in `DEQP_VK_QUERY_POOL_SRCS`.
- Several Level-3 files add their own finer-grained non-SC-only cases, especially `_device_address` or dynamic alpha-to-coverage variants, but those do not change the root `query_pool` child list.
