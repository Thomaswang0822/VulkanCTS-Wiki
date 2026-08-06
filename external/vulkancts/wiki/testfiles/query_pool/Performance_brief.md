# Understanding Brief: performance_query

## One-Sentence Test Purpose

This test checks that `VK_KHR_performance_query` counters can be enumerated, placed in single or simultaneous query pools, executed through all required profiling passes, and returned through the supported retrieval path.

## Background Knowledge

### Performance-query pools

A performance-query pool selects counters for one queue family. A device may need several submissions to collect all selected counters, so each submission carries a distinct pass index in `VkPerformanceQuerySubmitInfoKHR`.

Why it matters here:
- A recorded workload must run once for each pass reported by `vkGetPhysicalDeviceQueueFamilyPerformanceQueryPassesKHR`.
- The tests select only counters whose scope is not `VK_PERFORMANCE_COUNTER_SCOPE_COMMAND_BUFFER_KHR`, because their query boundaries surround a draw or dispatch rather than the whole command buffer.

### Retrieving query results

The host can call `vkGetQueryPoolResults`, or a command buffer can copy results to a transfer-destination buffer with `vkCmdCopyQueryPoolResults`. The latter path is conditional on `allowCommandBufferQueryCopies`.

Why it matters here:
- The same query workload covers both retrieval mechanisms.
- The check detects unwritten result slots, rather than assigning a numeric meaning to vendor-specific counter values.

## One Concrete Example

The `query_compute_copy` test selects eligible counters, creates one performance query pool, and resets its only query. It records `vkCmdBeginQuery`, a `2 x 2 x 2` dispatch, and `vkCmdEndQuery`. The CTS submits that command buffer once for each required pass. It then records `vkCmdCopyQueryPoolResults` to a host-visible buffer, waits for completion, and compares each result element with the random nonzero data that initially filled the buffer.

## End-to-End Test Flow

```text
[host] enumerate counters for the CTS universal queue family and remove command-buffer-scope counters
[host] choose all eligible counters for one pool, or alternate counter sets for two pools
[host] create the performance query pool or pools and obtain the required pass count
[host] acquire the profiling lock and reset the pool queries
[host] record a queried graphics draw or compute dispatch
[host] submit the recorded workload once for every required pass, changing the pass index
[host] obtain results through vkGetQueryPoolResults or vkCmdCopyQueryPoolResults
[host] fail if any enabled-counter result slot retains its initial random bytes
```

## Generated Test Artifacts and Bound Resources

### Generated or loaded program artifacts

The graphics variants build simple vertex and fragment shaders for a triangle draw. The compute variants build a shader that increments entries in a storage buffer. These programs provide work inside the query interval; the test does not interpret the counter values as shader outputs.

### Bound resources and memory objects

| Resource | Created/configured by host? | Bound to GPU? | Read/written by device? | Read back by host? | Why it matters |
|----------|-----------------------------|---------------|-------------------------|--------------------|----------------|
| Performance query pool | yes | yes | query commands write results | yes | Holds the selected counter results. |
| Result buffer | yes | yes in copy mode | transfer writes it | yes | Starts with random bytes so the test can detect an unwritten slot. |
| Graphics color image | yes | yes | graphics pipeline writes it | no | Supplies a minimal draw workload. |
| Compute storage buffer | yes | yes | compute shader writes it | no | Supplies a minimal dispatch workload. |

## What Is Checked

- Enumeration cases check incomplete enumeration, count consistency, unique counter UUIDs, valid scope/storage/unit enums, and permitted description flags for every matching graphics or compute queue family that reports counters.
- Single-pool cases check one queried draw or dispatch and every enabled result element.
- Multi-pool cases use two pools with complementary alternating counter selections and verify each pool separately.
- Query cases check whether each output element changed, not whether the counter has a particular value.

## Behavior Parameter Identification

> **Behavior parameter:** test behavior
>
> **Candidate values:** `enumerate_and_validate`, `query`, `multiple_pools`

A second execution axis selects `graphic` or `compute`; the `_copy` suffix selects command-buffer copying only for query-execution behavior.

## What Failure Means

### Failure Cause Mapping

| If this behavior parameter value fails | Possible failure cause(s) |
|----------------------------------------|---------------------------|
| `enumerate_and_validate` | Counter enumeration count or incomplete-result handling is inconsistent, metadata contains duplicate UUIDs or invalid enum values, or description flags contain bits outside the permitted set. |
| `query` | Pool creation, reset, profiling-pass submission, query execution, or the selected result-retrieval path leaves an enabled result slot unwritten. |
| `multiple_pools` | Simultaneous pool support, alternating counter selection, independent query execution, or independent result retrieval leaves a result slot unwritten. |

## Important Variations and Special Cases

- Registration creates twelve leaves: three behaviors by two workload types, each with and without `_copy`.
- The `_copy` suffix also appears on enumeration leaves because the shared registration loop adds it, but enumeration instances do not retrieve query results.
- `graphic` and `compute` choose a workload class. Actual query execution still uses the CTS universal queue family.
- The source parent excludes the test family when `CTS_USES_VULKANSC` is defined.

## Source Mapping

| Topic | Source link | Why it matters |
|-------|-------------|----------------|
| Enumeration validation | [EnumerateAndValidateTest::iterate()](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L150-L239) | Defines the metadata checks. |
| Counter selection and pool creation | [QueryTestBase](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L273-L378) | Filters scopes, selects counters, and gets the pass count. |
| Result overwrite check | [verifyQueryResults()](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L417-L466) | Defines both retrieval paths and the comparison rule. |
| Case registration and support | [QueryPoolPerformanceTests](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1221-L1386) | Defines support gates and all twelve leaves. |
| Extension metadata | [VK_KHR_performance_query.json](../../../scripts/src/extensions/VK_KHR_performance_query.json) | Records `performanceCounterQueryPools` as the extension's mandatory feature. |

## Questions / Risk Points for User Audit

- Is the distinction between a changed result slot and a semantically validated counter value clear?
- Is it clear that the multi-pool tests split the counter list and run one workload per pool?
- Is it clear that `_copy` does not change enumeration behavior?

## Conversion Notes for Final Wiki Rewrite

The final page should retain the three behavior values, both retrieval paths, the complementary two-pool selection, the universal-queue caveat, and the overwrite-detection semantics. It should use the failure-cause table unchanged and keep source navigation in an appendix.
