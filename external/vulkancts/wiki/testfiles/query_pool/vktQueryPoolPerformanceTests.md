# Performance Query Tests

Tests for Vulkan performance queries under `query_pool`. This page documents the `performance_query` Level-3 group registered from [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L49) and implemented in [`vktQueryPoolPerformanceTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp).

## Source

- [`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp)
- [`vktQueryPoolPerformanceTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp)
- [`vktQueryPoolPerformanceTests.hpp`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.hpp)

## Registration

| Item | Value |
|------|-------|
| Top-level parent | `query_pool` via [`createTests()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L59) |
| Level-3 group name | `performance_query` via [`QueryPoolPerformanceTests::QueryPoolPerformanceTests()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1351) |
| Child registration | [`queryPoolTests->addChild(new QueryPoolPerformanceTests(testCtx))`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L49) |
| Group population | [`QueryPoolPerformanceTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1356) |
| Vulkan SC split | Registered only when `CTS_USES_VULKANSC` is not defined, because the child registration is inside [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L48) |

## Summary

The `performance_query` group covers three logical behaviors for `VK_KHR_performance_query`: counter enumeration and metadata validation, single-pool query execution, and multi-pool query execution. Each behavior is instantiated for graphics and compute queues, and then duplicated for host-side result retrieval and command-buffer copy retrieval. The tests do not attempt to validate the semantic meaning of individual counter values; instead, they verify that supported counters can be enumerated, that query pools can be created and submitted across all required profiling passes, and that the implementation actually writes result data into the destination memory.

## Test Hierarchy

```text
query_pool
└── performance_query
    ├── enumerate_and_validate_graphic
    ├── enumerate_and_validate_compute
    ├── query_graphic
    ├── query_compute
    ├── multiple_pools_graphic
    ├── multiple_pools_compute
    ├── enumerate_and_validate_graphic_copy
    ├── enumerate_and_validate_compute_copy
    ├── query_graphic_copy
    ├── query_compute_copy
    ├── multiple_pools_graphic_copy
    └── multiple_pools_compute_copy
```

All twelve leaf cases are registered in the loop inside [`QueryPoolPerformanceTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1369).

## Registered Families

### Copy-mode axis

The outer registration loop defines two result-transfer modes in [`copyCases`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1359):

| Mode | `copyResults` | Name suffix | Result path |
|------|---------------|-------------|-------------|
| Host-get mode | `false` | none | [`vkGetQueryPoolResults`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L449) |
| Command-copy mode | `true` | `_copy` | [`vkCmdCopyQueryPoolResults`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L440) |

This suffix applies uniformly to enumeration, single-pool, and multiple-pool cases.

### Queue axis

Every logical case is generated for two queue classes:

| Queue flavor | Flag passed to constructor | Name fragment |
|--------------|----------------------------|---------------|
| Graphics | `VK_QUEUE_GRAPHICS_BIT` | `graphic` |
| Compute | `VK_QUEUE_COMPUTE_BIT` | `compute` |

The queue flag is stored in [`QueryPoolPerformanceTest`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1228) and controls both support checks and the concrete instance type returned by [`QueryPoolPerformanceTest::createInstance()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1241).

### 1. Enumeration-and-validation family

The first pair of registrations per copy mode produces:

- `enumerate_and_validate_graphic`
- `enumerate_and_validate_compute`
- `enumerate_and_validate_graphic_copy`
- `enumerate_and_validate_compute_copy`

These cases instantiate [`EnumerateAndValidateTest`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L131), which walks all queue families matching the requested queue flag and validates the performance-counter metadata returned by [`enumeratePhysicalDeviceQueueFamilyPerformanceQueryCountersKHR`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L163).

Validation covers:

| Check | Source |
|-------|--------|
| Incomplete read path returns `VK_INCOMPLETE` when only `counterCount - 1` slots are supplied | [`EnumerateAndValidateTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L175) |
| Final counter count matches the advertised count | [`EnumerateAndValidateTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L186) |
| Counter UUIDs are unique | [`EnumerateAndValidateTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L193) |
| Counter `scope`, `storage`, and `unit` enums are inside valid ranges | [`EnumerateAndValidateTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L203) |
| Counter-description flags contain only `PERFORMANCE_IMPACTING` and `CONCURRENTLY_IMPACTED` bits | [`EnumerateAndValidateTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L225) |

Although `_copy` variants are registered for this family, the enumeration instance itself does not perform any result-copy operation. The suffix is present because the registration loop applies the same naming template to all test types.

### 2. Single-pool query family

The second pair of registrations per copy mode produces:

- `query_graphic`
- `query_compute`
- `query_graphic_copy`
- `query_compute_copy`

These instantiate either [`GraphicQueryTest`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L638) or [`ComputeQueryTest`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1014), depending on queue type.

The common flow is:

1. Build graphics or compute state objects.
2. Enumerate supported counters and filter out command-buffer-scope counters via [`QueryTestBase::setupCounters()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L273).
3. Create one performance query pool enabling every eligible counter through [`QueryTestBase::createQueryPool()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L304).
4. Acquire the profiling lock using [`ProfilingLockGuard`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L103).
5. Reset the pool, record one query around a draw or dispatch, and submit the same command buffer once per required pass reported by [`getPhysicalDeviceQueueFamilyPerformanceQueryPassesKHR`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L361).
6. Read or copy the results and verify that each destination item changed from its randomized initial contents in [`QueryTestBase::verifyQueryResults()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L417).

### 3. Multiple-pools family

The final pair of registrations per copy mode produces:

- `multiple_pools_graphic`
- `multiple_pools_compute`
- `multiple_pools_graphic_copy`
- `multiple_pools_compute_copy`

These instantiate either [`GraphicMultiplePoolsTest`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L763) or [`ComputeMultiplePoolsTest`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1113).

The difference from the single-pool family is that the test allocates two query pools:

- one enabling counters selected with offset `0`, stride `2`; and
- one enabling counters selected with offset `1`, stride `2`.

That split is configured by the paired calls to [`createQueryPool(0, 2)`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L788) / [`createQueryPool(1, 2)`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L788) for graphics and again in [`ComputeMultiplePoolsTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1141) for compute. Each pool wraps its own draw or dispatch region, and each pool is verified independently after submission.

## Parameter Dimensions

### Test-type axis

[`TestType`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1221) defines the three top-level behaviors:

| Enum | Meaning | Registered names |
|------|---------|------------------|
| `TT_ENUMERATE_AND_VALIDATE` | Metadata enumeration / validation only | `enumerate_and_validate_*` |
| `TT_QUERY` | Single performance query pool | `query_*` |
| `TT_MULTIPLE_POOLS` | Two performance query pools in one test | `multiple_pools_*` |

### Counter-selection logic

[`QueryTestBase::createQueryPool()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L304) chooses enabled counters using offset/stride sampling over the filtered counter list:

| Call form | Effective selection |
|-----------|---------------------|
| `createQueryPool(0, 1)` | Enable every eligible counter |
| `createQueryPool(0, 2)` | Enable alternating counters starting from the first selected position |
| `createQueryPool(1, 2)` | Enable the complementary alternating subset |

Counters with `VK_PERFORMANCE_COUNTER_SCOPE_COMMAND_BUFFER_KHR` are removed before selection because these tests do not place query begin/end exactly at command-buffer boundaries; see [`QueryTestBase::setupCounters()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L291).

### Pass-count handling

Performance queries may require multiple submissions. The file stores the number of required passes in [`m_requiredNumerOfPasses`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L260), fills it using [`getPhysicalDeviceQueueFamilyPerformanceQueryPassesKHR`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L361), and then submits the workload once per pass with [`VkPerformanceQuerySubmitInfoKHR`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L737) or [`VkPerformanceQuerySubmitInfoKHR`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1087).

## Queue-Specific Execution Paths

### Graphics path

The graphics variants build a minimal render pipeline in [`GraphicQueryTestBase::initStateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L505):

- one `32x32` RGBA8 color attachment;
- a simple triangle-list pipeline with one vertex attribute;
- a vertex buffer containing three vertices.

The single-pool graphics case wraps one render pass with one query in [`GraphicQueryTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L650). The multiple-pool graphics case repeats the render-pass-and-draw sequence for two distinct pools in [`GraphicMultiplePoolsTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L775).

### Compute path

The compute variants build a storage-buffer-backed compute pipeline in [`ComputeQueryTestBase::initStateObjects()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L914):

- a descriptor set with one storage buffer;
- a compute shader writing into `sb_out.values[]`;
- a host-visible buffer plus a host-read barrier.

The single-pool compute case wraps one dispatch (`2 x 2 x 2`) with one query in [`ComputeQueryTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1026). The multiple-pool compute case records two queried dispatches, one per pool, in [`ComputeMultiplePoolsTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1125).

## Support Requirements

| Requirement | When needed | Source |
|------------|-------------|--------|
| `VK_KHR_performance_query` device functionality | All cases | [`QueryPoolPerformanceTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1298) |
| `performanceCounterQueryPools` feature | All cases | [`QueryPoolPerformanceTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1302) |
| `performanceCounterMultipleQueryPools` feature | `multiple_pools_*` cases | [`QueryPoolPerformanceTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1306) |
| `allowCommandBufferQueryCopies` property | `_copy` variants | [`QueryPoolPerformanceTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1321) |
| At least one reported performance counter | All cases, otherwise `QualityWarning` | [`QueryPoolPerformanceTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1313) |
| At least one counter whose scope is not `COMMAND_BUFFER` | All non-enumeration cases | [`QueryPoolPerformanceTest::checkSupport()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1325) |

### Queue-family behavior

For enumeration tests, the requested queue flag is used to scan every queue family and validate every matching family, as implemented in [`EnumerateAndValidateTest::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L157).

For actual query execution, however, the file always uses the universal queue family from the CTS context for counter enumeration, pool creation, and submission; see [`QueryTestBase::setupCounters()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L277) and [`QueryTestBase::createQueryPool()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L310). The `graphic` / `compute` distinction therefore selects the workload type rather than dynamically rebinding to separate queue-family indices.

## Verification Methods

### Enumeration verification

Enumeration cases verify API metadata consistency only. They do not execute any query workload or compare counter values.

### Result-write verification

The query-execution families intentionally avoid checking the semantic meaning of each counter. Instead, [`QueryTestBase::verifyQueryResults()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L417) performs a robust write-detection check:

1. Create a result vector filled with non-zero random bytes via [`createResultsVector()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L380).
2. Copy those bytes into a host-visible output buffer via [`createResultsBuffer()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L398).
3. Read results with either host-get or command-copy mode.
4. Compare every `VkPerformanceCounterResultKHR` slot against the original randomized contents.
5. Fail if any slot is unchanged, because that implies the implementation did not write that result element.

This means the test validates that all enabled counters produce output and that the copy/get path touches the expected memory region, without assuming specific counter magnitudes.

## Vulkan SC and Extension-Specific Notes

- The whole `performance_query` group is absent from Vulkan SC because the parent registration is inside [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L48).
- The file depends specifically on `VK_KHR_performance_query` features and properties, including the profiling lock acquired with [`acquireProfilingLockKHR`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L116).
- `_copy` variants additionally depend on the extension property allowing command-buffer query copies, so they are an extension-property split rather than a separate subgroup naming convention.

## Notes

- The registration loop also appends `_copy` to enumeration-only tests, even though those instances do not copy results; this is an artifact of the shared naming harness in [`QueryPoolPerformanceTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L1369).
- Single-pool and multiple-pool tests always execute all required profiling passes by resubmitting the same recorded workload with a changing [`VkPerformanceQuerySubmitInfoKHR`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp#L737).
- This page documents only the Level-3 file represented by [`vktQueryPoolPerformanceTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp).