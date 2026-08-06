## Overview

**Core question:** Do pipeline-statistics queries report the expected work and result state across recording, reset, and retrieval paths?

- This page covers `statistics_query`, implemented by [`vktQueryPoolStatisticsTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp), under the `query_pool` test category.
- The family creates `VK_QUERY_TYPE_PIPELINE_STATISTICS` pools for compute, input-assembly, shader, clipping, and tessellation counters.
- It varies command-buffer mode, result transport, record width, reset timing, and selected graphics or compute work.
- The source also contains separate multi-counter and multiple-geometry-statistics cases.

## Background Knowledge

A pipeline-statistics query pool selects one or more `VkQueryPipelineStatisticFlagBits` at creation. Vulkan writes results in the selected-bit order. [Pipeline Statistics Queries](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats) defines the query type and selected counters.

A result request can use 32-bit or 64-bit integers. `VK_QUERY_RESULT_WITH_AVAILABILITY_BIT` appends an availability integer after each query's result values; its width matches the requested result width. The specification describes this per-query layout and the meaning of a zero availability value in [Pipeline Statistics Queries](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats).

With `VK_QUERY_RESULT_PARTIAL_BIT`, an unavailable query can return an intermediate value between zero and its final value. Without that flag, unavailable result values are undefined. See [partial results](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats).

## Registration Hierarchy

```text
query_pool.statistics_query
├── compute_shader_invocations
├── input_assembly_vertices
├── input_assembly_primitives
├── vertex_shader_invocations
├── fragment_shader_invocations
├── geometry_shader_invocations
├── geometry_shader_primitives
├── clipping_invocations
├── clipping_primitives
├── tes_control_patches
├── tes_evaluation_shader_invocations
├── vertex_only
├── host_query_reset
├── reset_before_copy
├── reset_after_copy
├── multiple_queries
└── multiple_geom_stats
```

[`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6211) creates these 17 direct intermediate nodes. [`query-pool.txt`](../../../mustpass/main/vk-default/query-pool.txt) contains 17,769 registered leaves below `dEQP-VK.query_pool.statistics_query`; the tree above is therefore a compact view of a much larger generated matrix.

## Parameter Dimensions and Observed Values

| Dimension | Values or groups | Effect on the check |
|---|---|---|
| Statistic | Compute; input assembly vertices and primitives; vertex, fragment, geometry, clipping, and tessellation counters | Selects the count expected from the submitted work. |
| Command-buffer mode | `primary`, `secondary`, `secondary_inherited` | Changes where commands are recorded and whether inheritance information is used. |
| Result transport | `vkGetQueryPoolResults`, `vkCmdCopyQueryPoolResults`, and selected `vkCmdCopyQueryPoolResultsToMemoryKHR` paths | Changes the destination and decoding route. |
| Result layout | 32-bit or 64-bit values, optional availability, destination offset, valid or zero stride | Changes record size, placement, and decoding. |
| Reset workflow | Normal, host reset, reset before copy, reset after copy | Determines whether CTS expects a completed value or an unavailable result. |
| Work shape | Compute group and local sizes; graphics topology, stage configuration, clear operation, and repeated draws | Supplies the expected count or lower bound. |

The general generator iterates host-get and command-copy modes, 32-bit and 64-bit results, and destination-offset choices. It suppresses destination-offset cases for host retrieval because that API has no destination-offset parameter. It permits zero stride only for command copies. See [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6388).

The standard graphics repeat vector is `{1, 3, 5, 8, 15, 24}`. The test uses it to check scalable counter behavior rather than treating one draw as evidence for all counts. See [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6225).

### Counter families: selected pipeline statistics

The ordinary direct intermediate nodes name the requested statistic. `compute_shader_invocations` dispatches a compute workload. The graphics nodes cover input assembly, vertex, fragment, geometry, clipping, tessellation-control, and tessellation-evaluation statistics. `vertex_only` is a reduced-pipeline subset for input-assembly and vertex counters.

Topology expands the graphics cases across point, line, triangle, adjacency, and patch-list forms. Patch-list cases enable tessellation and add patch-size and primitive-count variants. Geometry and tessellation paths use their own expected counts because their counters measure different pipeline stages.

### Command-buffer modes: placement and inheritance

`PRIMARY` records the test in a primary command buffer. `SECONDARY` moves part of the work into a secondary command buffer. `SECONDARY_INHERITED` also supplies inherited pipeline-statistics information through `VkCommandBufferInheritanceInfo`. The source's `beginSecondaryCommandBuffer()` sets that inheritance field before secondary recording. See [`beginSecondaryCommandBuffer()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L400).

### Result transport: host reads, copies, and records

Host retrieval uses `vkGetQueryPoolResults`; command-copy cases use `vkCmdCopyQueryPoolResults`. The source decodes both paths into shared result-vector forms. `cmdCopyQueryPoolResults()` selects the buffer command or, when a device address is supplied in non-SC builds, `vkCmdCopyQueryPoolResultsToMemoryKHR`. See [`cmdCopyQueryPoolResults()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L264).

For availability records, the source uses `(value, availability)` pairs. A requested destination offset leaves a sentinel-filled record before the copied result. The reset-buffer verifier fails if that preceding record changes. See [`StatisticQueryTestInstance::verifyUnavailable()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L589).

### Reset workflows: result lifetime

The base families reset the pool in the command buffer before issuing the query. `host_query_reset` resets from the host, `reset_before_copy` resets after query completion commands but before the copy, and `reset_after_copy` copies first and resets afterward. The final two modes exercise copy ordering and unavailable-query reporting separately.

## Behavior Parameters

The behavioral axes are the selected statistic, command-buffer mode, reset workflow, and result layout. Topology and stage configuration determine an expected count, but they do not change the query protocol.

### Normal and reset-after-copy: completed result

For a normal workflow, CTS resets, begins the query, submits work, ends the query, waits, and reads the counter. Reset-after-copy adds a command-buffer copy before the reset, then checks the copied completed value. Compute cases require an exact invocation total. Many graphics cases use an expected minimum because rasterization and stage behavior can make a conservative bound more suitable.

### Host reset: completed then unavailable

Host-reset cases first read a completed value with availability enabled. CTS requires the expected value and a nonzero availability field. It then calls `vkResetQueryPool`, requests the result without wait or partial flags, and requires `VK_NOT_READY` with availability zero. The source retains the prior value in the local result storage and checks that the unavailable call did not overwrite it. See [`ComputeInvocationsTestInstance::executeTest()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L881).

### Reset before copy: unavailable copy record

These cases end the query, reset it in the command buffer, then copy the result with 64-bit values and availability. The expected copied availability is zero. The test also checks any destination-offset sentinel, so a correct availability value cannot hide a mispositioned copy.

### Multiple queries and multiple geometry statistics

`multiple_queries` enables input-assembly vertex and primitive statistics plus either fragment or vertex invocations. It combines partial and wait flags, host retrieval or command copying, destination offset, and selected zero-stride cases. The generator omits partial-plus-wait combinations because a query intentionally left unissued could wait indefinitely, and it omits zero stride for partial multi-query copies. See [`QueryPoolStatisticsTests::init()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L8942).

`multiple_geom_stats` has eight leaves: host get or copy, availability off or on, and inheritance off or on. It enables both geometry-shader invocations and geometry-shader primitives, checks each result item against a lower bound, then checks the rendered color image. See [`MultipleGeomStatsTestInstance::iterate()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L4901).

## Shader Analysis

The source generates small compute, vertex, tessellation, geometry, and fragment shaders for different counters. Their role is to create controlled work at the pipeline stage named by the query. The test does not use one stable representative shader across the family, so this page does not present a single shader or SPIR-V walkthrough. The result checks, not shader output alone, define the statistics-query assertion.

The compute shader writes each global invocation index to a storage buffer. CTS checks that buffer after submission as an independent confirmation that the dispatched work ran. See [`QueryPoolComputeStatsTest::initPrograms()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L4033).

## Runtime Execution and Result Checking

1. CTS creates a pipeline-statistics query pool with the requested statistic bit or bit set.
2. It records the relevant reset, query begin, workload, query end, optional result copy, and barriers in primary or secondary command buffers.
3. It submits the primary command buffer and waits for completion.
4. It obtains results from host memory or the copied host-visible buffer.
5. It applies the mode-specific check: exact value, lower bound, availability state, result code, record placement, or image output.

Compute validation compares the query result with the product of local and group dimensions, then checks every storage-buffer element. See [`ComputeInvocationsTestInstance::executeTest()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L878).

The multi-statistic validator decodes each query's enabled statistic bits in bit order. It requires availability after a waited non-partial request, rejects available values below the expected minimum, and bounds unavailable partial values by the expected maximum. See [`VertexShaderMultipleQueryTestInstance::checkResult()`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L4545).

## Failure Meaning

### Failure Cause Mapping

| Observed failure | Check that reports it | What it points to |
|---|---|---|
| Exact compute count differs | Compute result comparison | Wrong compute-statistic accounting or result retrieval. |
| Graphics value is below its minimum | Per-statistic graphics validation | The selected stage did not contribute the expected work, or result decoding selected the wrong item. |
| Waited result has zero availability | Multi-query availability check | Completion or availability reporting is incorrect. |
| Host reset returns another status or nonzero availability | Host-reset validation | Host query reset or unavailable-result behavior is incorrect. |
| Reset-before-copy record is available | Reset-buffer validation | Reset and copy ordering is incorrect. |
| Offset sentinel changes | Destination-offset validation | The command copy wrote at the wrong location. |
| Geometry count passes but image differs | Geometry image comparison | The draw path itself did not produce the expected output. |

### Cause Analysis

A pipeline counter mismatch does not identify a single driver component. The source distinguishes exact workloads from lower-bound graphics cases because counters reflect the selected stage and pipeline behavior. A failure must therefore be interpreted against the queried statistic, active stages, topology, and result flags.

Availability and reset failures have narrower meaning. The Vulkan specification says availability zero means the result is not yet available, and specifies the layout that follows each query's result values. The host-reset and reset-before-copy branches directly test those rules. A destination-offset failure is a data-placement failure even if the copied counter itself looks correct.

## Case Pruning

The source intentionally prunes invalid or redundant combinations:

- host retrieval does not receive destination-offset variants;
- zero stride appears only in command-copy configurations;
- reset-after-copy exists only where a command copy occurs;
- partial-plus-wait multiple-query cases are skipped to avoid an indefinitely unavailable query;
- partial multi-query cases skip zero stride;
- `_device_address` cases are sampled rather than exhaustive and are excluded by `#ifndef CTS_USES_VULKANSC`;
- point-mode isoline tessellation cases are skipped to limit the matrix.

These are source-level matrix decisions, not missing mustpass entries. The mustpass file still records the generated leaves that remain after pruning.

## Key Takeaways

- `statistics_query` verifies both pipeline counting and query-result protocol behavior.
- The main behavioral axes are statistic selection, recording mode, reset timing, and result-record layout.
- The result checks cover completed values, unavailable states, availability fields, copied-buffer placement, and selected independent workload outputs.
- Feature gates separate unsupported hardware configurations from failures in supported paths.

## Source Reference Appendix

- [Statistics-query implementation and generator](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L6199)
- [Common statistics and host-reset support checks](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L505)
- [Query-pool construction and result helpers](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp#L177)
- [Canonical mustpass entries](../../../mustpass/main/vk-default/query-pool.txt)
- [Vulkan query result retrieval rules](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats)
