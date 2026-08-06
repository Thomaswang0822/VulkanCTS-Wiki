## Overview

**Core question:** Which Vulkan query-pool behaviors does the `query_pool` test category exercise, and how are those behaviors divided among its implementation-bearing test families?

- The category registers seven direct test families: `occlusion_query`, `statistics_query`, `performance_query`, `maintenance7`, `concurrent_queries`, `frag_invocations`, and `discard`.
- The first five families cover query retrieval, reset, pipeline statistics, performance counters, timestamp width rules, and simultaneous query use. The last two focus on fragment invocation accounting and occlusion behavior around coverage-discarding operations.
- The dispatcher only builds the category tree. The implementation-bearing behavior is documented on the linked Level-3 pages below.

## Background Knowledge

- A Vulkan query pool stores device-generated results that can be read by the host with `vkGetQueryPoolResults` or copied to a buffer with `vkCmdCopyQueryPoolResults`. A result may also carry an availability value, and result width and `stride` determine the destination layout.
- Query types observe different events. Occlusion queries count passing samples, pipeline statistics queries count selected pipeline events, timestamp queries record device time at a pipeline stage, and performance queries expose implementation-defined counter values and metadata.
- A query is normally reset before reuse, and command-buffer recording order determines which work falls between query begin/end commands or follows a timestamp write. Secondary command buffers add inheritance rules when an active query spans `vkCmdExecuteCommands`.

## Registration Hierarchy

```text
query_pool
├── occlusion_query
├── statistics_query
├── performance_query
├── maintenance7
├── concurrent_queries
├── frag_invocations
└── discard
```

The top-level tree is created by [`createChildren()`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42-L55). `performance_query` and `maintenance7` are attached only when `CTS_USES_VULKANSC` is not defined. The other five families are attached for both Vulkan and Vulkan SC builds, subject to their own support checks.

## Test Families

| Test family | Main question | Level-3 page | Build scope |
|---|---|---|---|
| `occlusion_query` | Do conservative and precise occlusion queries produce the expected visibility and availability results through host, copy, reset, stride, and rendering variants? | [Occlusion](../testfiles/query_pool/Occlusion.md) | Vulkan and Vulkan SC |
| `statistics_query` | Do selected compute and graphics pipeline-statistics counters match the recorded workload across command-buffer and retrieval modes? | [Statistics](../testfiles/query_pool/Statistics.md) | Vulkan and Vulkan SC |
| `performance_query` | Can performance counters be enumerated and queried through single-pool and multi-pool host-get or copy paths? | [Performance](../testfiles/query_pool/Performance.md) | Vulkan only |
| `maintenance7` | Does a 32-bit timestamp result follow the required relationship to its 64-bit result with and without the `maintenance7` feature? | [Maintenance7](../testfiles/query_pool/Maintenance7.md) | Vulkan only |
| `concurrent_queries` | Can multiple query types measure separate slots in one primary or secondary-command-buffer workload without interference? | [Concurrent](../testfiles/query_pool/Concurrent.md) | Vulkan and Vulkan SC |
| `frag_invocations` | Do occlusion and fragment-invocation queries reflect a full-screen draw across shader variants and command-buffer modes? | [FragInvocation](../testfiles/query_pool/FragInvocation.md) | Vulkan and Vulkan SC |
| `discard` | Do occlusion results follow fragment discard, sample-mask, alpha-to-coverage, and early-fragment-test ordering rules? | [Discard](../testfiles/query_pool/Discard.md) | Vulkan and Vulkan SC |

## Source Organization

The category dispatcher is [`vktQueryPoolTests.cpp`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp), with its declaration in [`vktQueryPoolTests.hpp`](../../modules/vulkan/query_pool/vktQueryPoolTests.hpp). The implementation sources are listed in [`CMakeLists.txt`](../../modules/vulkan/query_pool/CMakeLists.txt#L7-L27).

- The shared `DEQP_VK_VKSC_QUERY_POOL_SRCS` set contains occlusion, statistics, concurrent, fragment-invocation, discard, and dispatcher sources. These are compiled for both Vulkan and Vulkan SC.
- The Vulkan-only `DEQP_VK_QUERY_POOL_SRCS` set contains performance-query and maintenance7 sources. The dispatcher uses the same non-SC guard for their registration.
- Headers declare the individual factories and test classes; they do not add separate top-level registration branches.

## Cross-Family Reading Guide

Use the Level-3 pages for the detailed parameter matrices and validation contracts. Across the category, the most common comparison axes are:

- **Result path:** host result retrieval versus command-buffer copy, especially in `occlusion_query`, `statistics_query`, and `performance_query`.
- **Reset timing:** ordinary reset, host reset, reset before copy, and reset after copy.
- **Result width and layout:** 32-bit versus 64-bit values, optional availability, `stride`, and destination offsets.
- **Command-buffer mode:** primary, secondary, and inherited secondary recording.
- **Verification strength:** exact counts for precise cases versus non-zero or lower-bound checks where Vulkan or the test mechanism does not require one exact value.

These dimensions recur across implementations but do not imply one shared validation rule. Each Level-3 page defines the source-specific pass condition and support gates.

## Source Reference Appendix

| Topic | Source |
|---|---|
| Category registration | [`vktQueryPoolTests.cpp#L42-L61`](../../modules/vulkan/query_pool/vktQueryPoolTests.cpp#L42-L61) |
| Build split | [`CMakeLists.txt#L7-L35`](../../modules/vulkan/query_pool/CMakeLists.txt#L7-L35) |
| Query-pool semantics | [Vulkan Queries](../../../vulkan-docs/src/chapters/queries.adoc) |
| Historical query coverage | [`apitests.adoc#L427-L432`](../../../../doc/testspecs/VK/apitests.adoc#L427-L432) |
