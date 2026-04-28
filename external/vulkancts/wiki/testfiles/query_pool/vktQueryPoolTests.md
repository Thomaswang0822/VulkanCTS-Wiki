# Query Pool Tests — Root Registration

The `vktQueryPoolTests.cpp` file is the **registration dispatcher** for the entire Vulkan CTS `query_pool` category. It defines the top-level `query_pool` test group and populates it with child subgroups, each implemented in a separate source file.

## Source

[`vktQueryPoolTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp)

## Role

Central registration point. The [`createTests()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:59) factory function is called by the test package to create the top-level `query_pool` group. The [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:42) function inside the anonymous namespace adds all child subgroups.

## Registration Path

```text
vk-test-package → query_pool (createTests) → <children>
```

## Test Hierarchy

The `query_pool` category contains **7 child groups**. Two of them are Vulkan-only because their registrations are guarded by `#ifndef CTS_USES_VULKANSC` in the root dispatcher.

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
| `occlusion_query` | ✓ | ✓ | Always included in [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:46) |
| `statistics_query` | ✓ | ✓ | Always included in [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:47) |
| `performance_query` | ✓ | — | Registered only inside [`#ifndef CTS_USES_VULKANSC`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:48) |
| `maintenance7` | ✓ | — | Registered only inside the same non-SC block in [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:50) |
| `concurrent_queries` | ✓ | ✓ | Always included in [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:52) |
| `frag_invocations` | ✓ | ✓ | Always included in [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:53) |
| `discard` | ✓ | ✓ | Always included in [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:54) |

## Child Group Reference

| Group Name | Source File | Level-3 Doc |
|------------|------------|-------------|
| `occlusion_query` | [`vktQueryPoolOcclusionTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolOcclusionTests.cpp) | [vktQueryPoolOcclusionTests.md](vktQueryPoolOcclusionTests.md) |
| `statistics_query` | [`vktQueryPoolStatisticsTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp) | [vktQueryPoolStatisticsTests.md](vktQueryPoolStatisticsTests.md) |
| `performance_query` | [`vktQueryPoolPerformanceTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolPerformanceTests.cpp) | [vktQueryPoolPerformanceTests.md](vktQueryPoolPerformanceTests.md) |
| `maintenance7` | [`vktQueryMaintenance7Tests.cpp`](../../../modules/vulkan/query_pool/vktQueryMaintenance7Tests.cpp) | [vktQueryMaintenance7Tests.md](vktQueryMaintenance7Tests.md) |
| `concurrent_queries` | [`vktQueryPoolConcurrentTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolConcurrentTests.cpp) | [vktQueryPoolConcurrentTests.md](vktQueryPoolConcurrentTests.md) |
| `frag_invocations` | [`vktQueryPoolFragInvocationTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolFragInvocationTests.cpp) | [vktQueryPoolFragInvocationTests.md](vktQueryPoolFragInvocationTests.md) |
| `discard` | [`vktQueryPoolDiscardTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolDiscardTests.cpp) | [vktQueryPoolDiscardTests.md](vktQueryPoolDiscardTests.md) |

## Include-to-Registration Map

The top-level dispatcher includes one header per registered child implementation before wiring them into [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:42).

| Include | Registration | Notes |
|---------|--------------|-------|
| [`#include "vktQueryPoolOcclusionTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:28) | [`new QueryPoolOcclusionTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:46) | Always included |
| [`#include "vktQueryPoolStatisticsTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:29) | [`new QueryPoolStatisticsTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:47) | Always included |
| [`#include "vktQueryPoolPerformanceTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:30) | [`new QueryPoolPerformanceTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:49) | Registration is non-SC only |
| [`#include "vktQueryPoolConcurrentTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:31) | [`new QueryPoolConcurrentTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:52) | Always included |
| [`#include "vktQueryPoolFragInvocationTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:32) | [`createFragInvocationTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:53) | Factory-style group creation |
| [`#include "vktQueryMaintenance7Tests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:33) | [`createQueryMaintenance7Tests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:50) | Registration is non-SC only |
| [`#include "vktQueryPoolDiscardTests.hpp"`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:34) | [`createDiscardTests(testCtx)`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:54) | Factory-style group creation |

## Registration Order

The root file registers children in this exact order:

1. `occlusion_query`
2. `statistics_query`
3. `performance_query` *(VK only)*
4. `maintenance7` *(VK only)*
5. `concurrent_queries`
6. `frag_invocations`
7. `discard`

That order is defined directly by the sequential [`addChild()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:46) calls in [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:42).

## Notes

- The root dispatcher itself does not build any deeper subgroup hierarchy; it only delegates to the seven child factories or test-group classes listed above.
- Two child groups use direct `TestCaseGroup` subclasses (`occlusion_query`, `statistics_query`, `performance_query`, `concurrent_queries`), while three are factory-created groups (`maintenance7`, `frag_invocations`, `discard`). The distinction is visible in whether registration uses `new ...Tests(...)` or `create...Tests(...)` in [`createChildren()`](../../../modules/vulkan/query_pool/vktQueryPoolTests.cpp:46).
- The Vulkan / Vulkan SC split at this level is exact and limited to `performance_query` and `maintenance7`; no other top-level group names are altered or omitted by the root registration file.
