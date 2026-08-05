# query\_pool Rewrite Outline

## Scope

- Category: `query_pool`
- Old Level-2 page: `external/vulkancts/wiki/categories/query_pool.md`
- Old Level-3 directory: `external/vulkancts/wiki/testfiles/query_pool/`
- Source category directory: `external/vulkancts/modules/vulkan/query_pool/`

## Page Count

- Old Level-3 pages found: 8
- Registration-only dispatcher pages to fold into Level-2: 1 (`vktQueryPoolTests.cpp` is registration-only; its `createTests()` at `vktQueryPoolTests.cpp#L59` calls `createChildren()` at `vktQueryPoolTests.cpp#L42-L55` which only attaches the seven implementation subgroups via `addChild()`. The old page `vktQueryPoolTests.md` is a navigation-only dispatcher page and should be folded into the rewritten Level-2 page, not rewritten as a Level-3 page.)
- Implementation-bearing Level-3 pages to rewrite: 7
- Counted rewrite files for batching: 12
  - 5 Understanding Briefs
  - 7 rewritten Level-3 pages

Brief pre-judgment rationale: occlusion, statistics, performance, frag\_invocations, and discard all have nontrivial validation logic, multiple execution paths, or multiple distinct mechanisms that risk source-navigation documentation if rewritten directly. Maintenance7 is a single-property timestamp check. Concurrent has a clear core mechanism (no interference) with a contained slot-based verification rule.

## Dispatcher Decision

- `vktQueryPoolTests.cpp` should NOT be rewritten because it is registration-only. Its sole role is to construct the top-level `query_pool` group and attach the seven implementation subgroups through `createChildren()`. It contains no test cases of its own.
- Fold category-specific dispatcher facts into the rewritten Level-2 `query_pool` page:
  - direct category tree: `occlusion_query`, `statistics_query`, `performance_query`, `maintenance7`, `concurrent_queries`, `frag_invocations`, `discard`;
  - VK / VKSC split: `performance_query` and `maintenance7` are Vulkan-only (guarded by `#ifndef CTS_USES_VULKANSC`); the other five groups are shared;
  - source-to-family routing for each implementation file.

## Batch 1 — Occlusion, statistics, performance

Counted files: 6

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktQueryPoolOcclusionTests.md`   |    Yes | Covers result retrieval (host get vs command copy), reset workflows (normal, host reset, reset before/after copy), availability, stride, and clear/blit/resolve/no-attachment paths. Exact-vs-conservative verification split and the large case matrix risk source-navigation documentation. Hits nontrivial-validation and multiple-execution-path brief conditions.                      |
| `vktQueryPoolStatisticsTests.md`  |    Yes | Repeatedly instantiates PRIMARY, SECONDARY, and SECONDARY\_INHERITED command-buffer modes across compute and graphics counters, with host\_query\_reset / reset\_before\_copy / reset\_after\_copy subtrees and result-layout variations. The structural complexity makes it hard to summarize in a few sentences. Hits nontrivial-validation and multiple-execution-path brief conditions. |
| `vktQueryPoolPerformanceTests.md` |    Yes | `VK_KHR_performance_query`. Single-pool and multi-pool execution with host-get and command-copy paths, plus randomized destination-buffer overwrite detection. Multi-pool synchronization is nontrivial. Hits nontrivial-synchronization and nontrivial-validation brief conditions.                                                                                                        |

## Batch 2 — Maintenance7, concurrent, frag\_invocations, discard

Counted files: 6

| Old Level-3 page | Brief? | Reason |
|---|---:|---|
| `vktQueryMaintenance7Tests.md`       |     No | Single-property test: timestamp 32-bit vs 64-bit relationship with and without `VK_KHR_maintenance7`. Core property, execution flow, validation rule, and failure meaning are clear. Direct rewrite.                                                                                                                           |
| `vktQueryPoolConcurrentTests.md`     |     No | Core mechanism (concurrent queries should not interfere) and slot-based zero-vs-non-zero verification are clear. Splits into primary/secondary command buffer but the validation logic is contained. Direct rewrite.                                                                                                           |
| `vktQueryPoolFragInvocationTests.md` |    Yes | Multiple verification modes: exact full-screen counts for `occlusion`, lower-bound checks for `frag_invs`, fragment-shading-rate-derived minimum for flat-shader cases. Primary/secondary command-buffer splits and shader variants. Hits nontrivial-validation and shader-variant brief conditions.                           |
| `vktQueryPoolDiscardTests.md`        |    Yes | Multiple distinct mechanisms: fragment discard, sample mask, alpha-to-coverage, early-fragment-test, and depth-use combinations. Exact counts in `precise` branches, non-zero in `none` branches. maintenance5 properties and `extendedDynamicState3AlphaToCoverageEnable`. Hits multiple-distinct-mechanisms brief condition. |

## Level-2 Synthesis

After all batches finish and rewritten Level-3 pages stabilize:

- Rewrite `query_pool.md` as the compact Level-2 category gateway.
- Include folded dispatcher information: the seven direct children, the VK / VKSC split, and the `CMakeLists.txt` shared-vs-Vulkan-only source split.
- Route readers to the rewritten Level-3 pages.
- Avoid duplicating parameter matrices, support gates, and verification mechanics from Level-3 pages.
- After the ordinary Level-2 gateway sections are drafted, run the category Background Knowledge consolidation pass.

## Notes on Inspection Order

- The first Level-3 page inspected for this category should be `vktQueryPoolOcclusionTests.md` because it is the largest and most feature-rich subgroup, covering result retrieval, reset workflows, and command-buffer modes that recur in other files.
- The `vktQueryPoolTests.cpp`/`.hpp` dispatcher and header files have no Level-3 page after the fold; the rewritten Level-2 page must reference them for the registration tree.
- The VK / VKSC split is structural only for `performance_query` and `maintenance7`; the other groups handle support differences inside their own implementations, and the Level-2 page must state this accurately.

