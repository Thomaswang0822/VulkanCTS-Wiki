# Query Pool Tests -- Root Registration

The `vktQueryPoolTests.cpp` file is the **registration dispatcher** for the entire Vulkan CTS `query_pool` category. It defines the top-level `query_pool` test group and populates it with child subgroups, each implemented in a separate source file.

## Source

[`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp)

## Registration Hierarchy

```text
query_pool
├── occlusion_query (VK + VKSC)
├── statistics_query (VK + VKSC)
├── performance_query (VK only)
├── maintenance7 (VK only)
├── concurrent_queries (VK + VKSC)
├── frag_invocations (VK + VKSC)
└── discard (VK + VKSC)
```

The root dispatcher registers children in this exact order via sequential [`addChild()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L46) calls in [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42). Two child groups (`performance_query` and `maintenance7`) are Vulkan-only because their registrations are guarded by `#ifndef CTS_USES_VULKANSC` in the root dispatcher.

## Role

Central registration point. The [`createTests()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L59) factory function is called by the test package to create the top-level `query_pool` group. The [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42) function inside the anonymous namespace adds all child subgroups.

## Test Families

### occlusion_query -- Occlusion query tests (VK + VKSC)

Registered via [`new QueryPoolOcclusionTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L46). Always included. Implemented in [`vktQueryPoolOcclusionTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp). See [vktQueryPoolOcclusionTests.md](vktQueryPoolOcclusionTests.md).

### statistics_query -- Pipeline statistics query tests (VK + VKSC)

Registered via [`new QueryPoolStatisticsTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L47). Always included. Implemented in [`vktQueryPoolStatisticsTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp). See [vktQueryPoolStatisticsTests.md](vktQueryPoolStatisticsTests.md).

### performance_query -- Performance query tests (VK only)

Registered via [`new QueryPoolPerformanceTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L49). Registration is non-SC only, inside [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L48). Implemented in [`vktQueryPoolPerformanceTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp). See [vktQueryPoolPerformanceTests.md](vktQueryPoolPerformanceTests.md).

### maintenance7 -- Maintenance7 timestamp query tests (VK only)

Registered via [`createQueryMaintenance7Tests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L50). Registration is non-SC only, inside the same non-SC block. Factory-style group creation. Implemented in [`vktQueryMaintenance7Tests.cpp`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp). See [vktQueryMaintenance7Tests.md](vktQueryMaintenance7Tests.md).

### concurrent_queries -- Concurrent query type tests (VK + VKSC)

Registered via [`new QueryPoolConcurrentTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L52). Always included. Implemented in [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp). See [vktQueryPoolConcurrentTests.md](vktQueryPoolConcurrentTests.md).

### frag_invocations -- Fragment invocation query tests (VK + VKSC)

Registered via [`createFragInvocationTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L53). Always included. Factory-style group creation. Implemented in [`vktQueryPoolFragInvocationTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp). See [vktQueryPoolFragInvocationTests.md](vktQueryPoolFragInvocationTests.md).

### discard -- Discard-related occlusion query tests (VK + VKSC)

Registered via [`createDiscardTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L54). Always included. Factory-style group creation. Implemented in [`vktQueryPoolDiscardTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp). See [vktQueryPoolDiscardTests.md](vktQueryPoolDiscardTests.md).

## Include-to-Registration Map

The top-level dispatcher includes one header per registered child implementation before wiring them into [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42).

| Include | Registration | Notes |
|---------|--------------|-------|
| [`#include "vktQueryPoolOcclusionTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L28) | [`new QueryPoolOcclusionTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L46) | Always included |
| [`#include "vktQueryPoolStatisticsTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L29) | [`new QueryPoolStatisticsTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L47) | Always included |
| [`#include "vktQueryPoolPerformanceTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L30) | [`new QueryPoolPerformanceTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L49) | Registration is non-SC only |
| [`#include "vktQueryPoolConcurrentTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L31) | [`new QueryPoolConcurrentTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L52) | Always included |
| [`#include "vktQueryPoolFragInvocationTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L32) | [`createFragInvocationTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L53) | Factory-style group creation |
| [`#include "vktQueryMaintenance7Tests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L33) | [`createQueryMaintenance7Tests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L50) | Registration is non-SC only |
| [`#include "vktQueryPoolDiscardTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L34) | [`createDiscardTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L54) | Factory-style group creation |

## Notes

- The root dispatcher itself does not build any deeper subgroup hierarchy; it only delegates to the seven child factories or test-group classes listed above.
- Two child groups use direct `TestCaseGroup` subclasses (`occlusion_query`, `statistics_query`, `performance_query`, `concurrent_queries`), while three are factory-created groups (`maintenance7`, `frag_invocations`, `discard`). The distinction is visible in whether registration uses `new ...Tests(...)` or `create...Tests(...)` in [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L46).
- The Vulkan / Vulkan SC split at this level is exact and limited to `performance_query` and `maintenance7`; no other top-level group names are altered or omitted by the root registration file.
