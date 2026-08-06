## Core mechanism

Pipeline-statistics queries count work at selected pipeline points. This family checks that the counter selected at query-pool creation, the command-buffer recording arrangement, query reset sequence, and result transport path agree with the work the CTS submits.

## Why this page needs a brief

`statistics_query` has a large generated matrix rather than one execution path. It combines compute and graphics counters, three command-buffer modes, host and command-buffer resets, two result widths, host retrieval and command copying, and a few feature-gated paths. The same source also has dedicated multiple-query and multiple-geometry-statistics tests.

## Background knowledge

A pipeline-statistics query pool uses `VK_QUERY_TYPE_PIPELINE_STATISTICS` and names one or more `VkQueryPipelineStatisticFlagBits`. Query results appear in the bit order selected for the pool. The Vulkan specification describes the query type and pipeline-statistics semantics in [Pipeline Statistics Queries](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats).

`VK_QUERY_RESULT_WITH_AVAILABILITY_BIT` appends an availability integer after each query's result sequence. With availability enabled, `stride` covers the whole `(results, availability)` record. The specification defines this layout in [Query Result Retrieval](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats).

## Test structure

The source creates the `statistics_query` test family and attaches 17 direct intermediate nodes. The ordinary counter nodes cover compute invocations, input assembly, shader stages, clipping, and tessellation. `vertex_only`, `host_query_reset`, `reset_before_copy`, and `reset_after_copy` reorganize variants of those counter families. `multiple_queries` checks several statistic bits and availability records in one result layout. `multiple_geom_stats` uses a two-counter geometry query.

The canonical mustpass file contains 17,769 leaves below `dEQP-VK.query_pool.statistics_query`, including all 17 direct intermediate nodes. It is evidence of registered coverage, not a claim that each configuration is meaningful on hardware lacking its required feature.

## Behavior parameter identification

| Behavioral axis | Values exercised | Why it changes the test |
|---|---|---|
| Statistic being requested | Compute, input assembly, vertex, fragment, geometry, clipping, tessellation; selected multi-statistic sets | Determines the expected count and the order of values in a result record. |
| Recording mode | Primary, secondary, secondary inherited | Checks where query commands and counted work are recorded, including inherited query state. |
| Reset workflow | Normal command reset, host reset, reset before copy, reset after copy | Changes whether a valid result or an unavailable result is expected at readback. |
| Result transport and layout | `vkGetQueryPoolResults`, command copy, 32-bit or 64-bit values, availability, destination offset, valid or zero stride | Checks the API-visible record layout and buffer placement. |
| Graphics work shape | Topology, tessellation configuration, clear behavior, draw repeat count, color-attachment mode | Produces stage-specific expected lower bounds or scalable sequences. |

The test-case names expose many of these choices, for example `64bits_cmdcopyquerypoolresults_stride_zero_secondary_inherited` and `32bits_primary_cq`.

## Execution and validation model

Compute cases dispatch a shader that writes its global invocation index to a storage buffer. The expected compute statistic is `localSize.x * localSize.y * localSize.z * groupSize.x * groupSize.y * groupSize.z`; CTS also checks every storage-buffer element against its index. Graphics cases issue controlled draws, often for repeat counts `{1, 3, 5, 8, 15, 24}`, and compare counters to the expectation appropriate to the selected statistic.

For normal and reset-after-copy cases CTS reads a completed counter and compares it with the expected value. Host-reset cases first require a valid result and nonzero availability, then reset the pool on the host and call `vkGetQueryPoolResults` without wait or partial flags. CTS expects `VK_NOT_READY`, preserves the previous value in the local result storage, and expects availability zero. Reset-before-copy cases reset after ending the query but before copying it, then require copied availability zero. A sentinel-filled destination region detects a copy that ignored `dstOffset`.

The multi-statistic test uses input-assembly vertices, input-assembly primitives, and either fragment or vertex invocations. It covers partial and wait flags, command-copy variants, availability records, and selected invalid-looking zero-stride layouts where only one query is copied. The geometry test checks geometry invocations and generated primitives, then checks the color output as an independent confirmation that the draw executed.

## Support requirements

All cases require the `pipelineStatisticsQuery` feature. Host-reset cases also require `VK_EXT_host_query_reset` and `hostQueryReset`. Secondary inherited cases require `inheritedQueries`. Geometry and tessellation families require their matching core features. Compute-queue cases look for a queue family with the requested capabilities. `_device_address` cases require `VK_KHR_device_address_commands` and occur only in non-Vulkan-SC guarded registrations. A triangle-fan configuration may be skipped when `VK_KHR_portability_subset` reports `triangleFans` unavailable.

## Failure cause mapping

| Symptom | Source-level check | Likely class of problem |
|---|---|---|
| Counter is below its expected value | Exact compute comparison or graphics lower-bound check | Counted work did not contribute to the selected statistic, or the counter was read from the wrong record. |
| Completed query has zero availability | Waited result validation | Query completion or result-status reporting is wrong. |
| Host reset does not return `VK_NOT_READY` with availability zero | Host-reset readback validation | Host reset or unavailable-query result semantics are wrong. |
| Reset-before-copy record has nonzero availability | Sentinel and availability check | Reset timing or copied result layout is wrong. |
| Sentinel at `dstOffset` changes | Destination-offset check | Copy placement ignored the requested offset. |
| Secondary inherited variant is unsupported or miscounts | Feature gate and inherited command buffer execution | Inherited-query support or secondary-command-buffer state is wrong. |

## Evidence used

- Implementation and registration: [`vktQueryPoolStatisticsTests.cpp`](../../../modules/vulkan/query_pool/vktQueryPoolStatisticsTests.cpp).
- Mustpass registration: [`query-pool.txt`](../../../mustpass/main/vk-default/query-pool.txt).
- Vulkan result layout and availability semantics: [`queries.adoc`](../../../../vulkan-docs/src/chapters/queries.adoc#queries-pipestats).
